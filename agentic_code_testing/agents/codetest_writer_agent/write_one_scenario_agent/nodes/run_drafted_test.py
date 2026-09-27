from pathlib import Path
from typing import Literal

from langgraph.runtime import Runtime

from agentic_code_testing.agents.codetest_writer_agent.guardrails import find_violations
from agentic_code_testing.agents.codetest_writer_agent.pytest_runner import run_pytest_on_code
from agentic_code_testing.agents.codetest_writer_agent.typed_schemas import (
    CodeTestWriterContext,
    CodeTestWriterState,
)


def run_drafted_test(state: CodeTestWriterState, runtime: Runtime[CodeTestWriterContext]) -> dict:
    violations = find_violations(state.drafted_code)
    if violations:
        return {"blocked_reasons": violations}

    scenario = runtime.context.scenarios[state.scenario_idx]
    root_dir = Path(runtime.context.root_dir).resolve()

    result = run_pytest_on_code(
        code=state.drafted_code,
        scenario_id=scenario.scenario_id,
        attempt=state.attempt,
        root_dir=root_dir,
        scratch_dir_name=runtime.context.scratch_dir_name,
        timeout=runtime.context.pytest_timeout_s,
    )

    return {"run_result": result, "blocked_reasons": []}


ROUTE_AFTER_RUN_T = Literal["finalize", "classify_failure"]


def route_after_run(state: CodeTestWriterState) -> ROUTE_AFTER_RUN_T:
    if state.blocked_reasons:
        return "finalize"
    if state.run_result is not None and state.run_result.returncode == 0:
        return "finalize"
    return "classify_failure"
