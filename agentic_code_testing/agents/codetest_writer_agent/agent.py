import logging
import uuid
from pathlib import Path
from typing import Callable, Generator, Optional

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from agentic_code_testing.agents.codetest_writer_agent.utils.pytest_runner import clear_stale_scratch
from agentic_code_testing.agents.codetest_writer_agent.typed_schemas import (
    CodeTestWriterContext,
    CodeTestWriterState,
    TestWriteResult,
)
from agentic_code_testing.agents.codetest_writer_agent.write_one_scenario_agent.graph import builder as once_scenario_builder
from agentic_code_testing.agents.codetest_writer_agent.write_report.base import BaseTestWriter
from agentic_code_testing.agents.planner_agent.typed_schemas import Scenario
from agentic_code_testing.logging.pydantic_logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

DEFAULT_SCRATCH_DIR_NAME = ".codetest_writer_scratch"
MAX_CODE_CONTEXT_ROUNDS = 5


def invoke_codetest_writer_agent(
    llm,
    scenarios: list[Scenario],
    file_writer: BaseTestWriter,
    output_dir,
    root_dir: str,
    max_attempts: int = 3,
    max_scenarios: Optional[int] = None,
    code_context_resolver: Optional[Callable[[str], str]] = None,
) -> list[TestWriteResult]:
    """Blocking wrapper over `iter_codetest_writer_agent_steps` for callers that
    don't need to answer code-context questions across a network boundary
    (tests, scripts) -- resolves each question in-process via
    `code_context_resolver`."""
    gen = iter_codetest_writer_agent_steps(llm, scenarios, file_writer, output_dir, root_dir, max_attempts, max_scenarios)
    answer = None
    while True:
        try:
            question = gen.send(answer)
        except StopIteration as done:
            return done.value
        answer = code_context_resolver(question) if code_context_resolver else "No code context available."


def iter_codetest_writer_agent_steps(
    llm,
    scenarios: list[Scenario],
    file_writer: BaseTestWriter,
    output_dir,
    root_dir: str,
    max_attempts: int = 3,
    max_scenarios: Optional[int] = None,
) -> Generator[str, str, list[TestWriteResult]]:
    """Generator form of `invoke_codetest_writer_agent`: yields each
    code-context question as it comes up and expects the answer sent back via
    `.send()`, so a caller spanning multiple requests (an A2A executor) can
    pause and resume this exact point instead of resolving it in-process.
    Returns the final test-write-result list via `StopIteration.value`.

    `max_scenarios` caps how many scenarios are drafted (to bound token/time
    cost); pass None for no limit."""
    if max_scenarios is not None:
        scenarios = scenarios[:max_scenarios]

    logger.info("Starting codetest writer agent for %d scenario(s)", len(scenarios))

    clear_stale_scratch(Path(root_dir).resolve(), DEFAULT_SCRATCH_DIR_NAME)

    context = CodeTestWriterContext(
        llm=llm,
        scenarios=scenarios,
        root_dir=root_dir,
        max_attempts=max_attempts,
    )

    scenario_graph = once_scenario_builder.compile(checkpointer=InMemorySaver())

    results = []
    for idx, scenario in enumerate(scenarios):
        logger.info("Drafting test %d/%d: %s", idx + 1, len(scenarios), scenario.scenario_id)
        state = CodeTestWriterState(scenario_idx=idx)
        run_config = {"configurable": {"thread_id": str(uuid.uuid4())}}

        result = scenario_graph.invoke(state, config=run_config, context=context)
        rounds = 0
        while "__interrupt__" in result and rounds < MAX_CODE_CONTEXT_ROUNDS:
            question = result["__interrupt__"][0].value["question"]
            answer = yield question
            result = scenario_graph.invoke(Command(resume=answer), config=run_config, context=context)
            rounds += 1

        if "__interrupt__" in result:
            # Still stuck asking for context after MAX_CODE_CONTEXT_ROUNDS rounds --
            # give up on this scenario rather than crashing on a missing "status".
            logger.warning(
                "Scenario %s still awaiting code context after %d round(s); marking unresolved",
                scenario.scenario_id, rounds,
            )
            write_result = TestWriteResult(
                scenario_id=scenario.scenario_id,
                title=scenario.title,
                status="unresolved",
                attempts=0,
                notes=f"Gave up after {rounds} code-context round(s) without enough information to draft a test.",
            )
        else:
            write_result = TestWriteResult(
                scenario_id=scenario.scenario_id,
                title=scenario.title,
                status=result["status"],
                attempts=result["attempt"],
                test_code=result.get("drafted_code"),
                notes=result.get("notes", ""),
                classification=result.get("classification"),
            )
        logger.info("Scenario %s finished with status=%s after %d attempt(s)",
                    scenario.scenario_id, write_result.status, write_result.attempts)
        results.append(write_result)

    logger.info("Writing %d test result(s) to %s", len(results), output_dir)
    file_writer.write(results, output_dir)

    logger.info("Finished codetest writer agent")
    return results
