import logging
import uuid
from typing import Callable, Generator, Optional

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from agentic_code_testing.agents.user_story_agent.typed_schemas import StoryAgentState
from agentic_code_testing.agents.planner_agent.extract_ac_agent.typed_schemas import ExtractACAgentState
from agentic_code_testing.agents.planner_agent.extract_ac_agent.graph import builder as extract_ac_builder
from agentic_code_testing.agents.planner_agent.plann_one_ac_agent.graph import builder as planner_once_ac_builder
from agentic_code_testing.agents.planner_agent.typed_schemas import (
    PlannerAgentState,
    PlannerAgentContext,
    Scenario,
    SCENARIO_CATEGORIES,
)
from agentic_code_testing.agents.planner_agent.write_markdown.base import BaseScenarioWriter
from agentic_code_testing.logging.pydantic_logger import setup_logging
from agentic_code_testing.tracing.config import configure_tracing

setup_logging()
configure_tracing()
logger = logging.getLogger(__name__)

MAX_CODE_CONTEXT_ROUNDS = 5


def invoke_planning_agent(
    llm,
    user_story: StoryAgentState,
    file_writer: BaseScenarioWriter,
    output_dir,
    root_dir: str,
    max_acs: int | None = None,
    code_context_resolver: Optional[Callable[[str], str]] = None,
):
    """Blocking wrapper over `iter_planning_agent_steps` for callers that don't
    need to answer code-context questions across a network boundary (tests,
    scripts) -- resolves each question in-process via `code_context_resolver`."""
    gen = iter_planning_agent_steps(llm, user_story, file_writer, output_dir, root_dir, max_acs)
    answer = None
    while True:
        try:
            kind, payload = gen.send(answer)
        except StopIteration as done:
            return done.value
        if kind == "question":
            answer = code_context_resolver(payload) if code_context_resolver else "No code context available."
        else:
            answer = None


def iter_planning_agent_steps(
    llm,
    user_story: StoryAgentState,
    file_writer: BaseScenarioWriter,
    output_dir,
    root_dir: str,
    max_acs: int | None = None,
) -> Generator[tuple[str, str] | tuple[str, Scenario], str | None, list[Scenario]]:
    """Generator form of `invoke_planning_agent`: yields `("question", text)` for
    each code-context question and `("progress", scenario)` as soon as each
    scenario is generated, expecting the answer (or `None` for a progress ack)
    sent back via `.send()`. This lets a caller spanning multiple requests (an
    A2A executor) pause/resume at questions and push progress out incrementally
    instead of only surfacing results once everything is done. Returns the
    final scenario list via `StopIteration.value`."""
    logger.info("Starting planning agent for story_id=%s", user_story.story_id)

    state = ExtractACAgentState()
    context = PlannerAgentContext(llm=llm, user_story=user_story, root_dir=root_dir)

    extract_ac_graph = extract_ac_builder.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    logger.info("Extracting acceptance criteria for story_id=%s", user_story.story_id)
    result = extract_ac_graph.invoke(state, config=config, context=context)
    if "__interrupt__" in result:
        logger.info(
            "Acceptance criteria not found for story_id=%s; auto-accepting %d AI-generated criteria",
            user_story.story_id,
            len(result["acs"]),
        )
        # No human is available to review AI-generated criteria here, so auto-accept them.
        result = extract_ac_graph.invoke(Command(resume={"accepted": True}), config=config, context=context)

    acs = result["acs"]
    logger.info("Extracted %d acceptance criteria for story_id=%s", len(acs), user_story.story_id)

    if max_acs is not None:
        acs = acs[:max_acs]
        logger.info("Capping to %d acceptance criteria for story_id=%s", len(acs), user_story.story_id)

    context = context.model_copy(update={"acs": acs})

    planner_graph = planner_once_ac_builder.compile(checkpointer=InMemorySaver())

    all_scenarios = []
    for ac_idx in range(len(acs)):
        logger.info("Generating scenarios for AC %d/%d", ac_idx + 1, len(acs))
        code_context = None

        for category in SCENARIO_CATEGORIES:
            logger.info("AC %d: starting category '%s'", ac_idx + 1, category)
            state = PlannerAgentState(
                ac_idx=ac_idx,
                current_category=category,
                is_category_covered=False,
                coverage_reasoning="",
                code_context=code_context,
            )
            ac_config = {"configurable": {"thread_id": str(uuid.uuid4())}}

            category_scenarios: list[Scenario] = []
            stream_input = state
            rounds = 0
            while True:
                for chunk in planner_graph.stream(stream_input, config=ac_config, context=context, stream_mode="updates"):
                    if "__interrupt__" in chunk:
                        question = chunk["__interrupt__"][0].value["question"]
                        answer = yield ("question", question)
                        stream_input = Command(resume=answer)
                        rounds += 1
                        break
                    for node_name, node_update in chunk.items():
                        if node_name == "generate_senarios" and node_update.get("scenarios"):
                            new_scenario = node_update["scenarios"][-1]
                            category_scenarios.append(new_scenario)
                            yield ("progress", new_scenario)
                        elif node_name == "request_code_context" and "code_context" in node_update:
                            code_context = node_update["code_context"]
                else:
                    # Stream finished without hitting an interrupt: category done.
                    break

                if rounds >= MAX_CODE_CONTEXT_ROUNDS:
                    break

            logger.info(
                "Generated %d scenarios for AC %d/%d category '%s'",
                len(category_scenarios), ac_idx + 1, len(acs), category,
            )
            all_scenarios.extend(category_scenarios)

    logger.info("Writing %d scenarios to markdown at %s", len(all_scenarios), output_dir)
    file_writer.write(all_scenarios, output_dir)

    logger.info("Finished planning agent for story_id=%s", user_story.story_id)
    return all_scenarios