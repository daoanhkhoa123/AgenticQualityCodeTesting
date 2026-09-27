from typing import Literal

from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from agentic_code_testing.agents.codetest_writer_agent.structured_output import invoke_structured
from agentic_code_testing.agents.codetest_writer_agent.typed_schemas import (
    CodeTestWriterContext,
    CodeTestWriterState,
    FailureClassification,
)

MAX_OUTPUT_CHARS = 4_000

CLASSIFY_FAILURE_PROMPT = """
This drafted pytest test failed. Decide whether the bug is in the TEST itself
(bad import, bad assertion, wrong fixture usage, signature mismatch with the
real code -- something a better-written test would avoid) or in the SOURCE
code under test (the code doesn't actually behave the way the scenario expects
it to).

Scenario:
Title: {title}
Description: {description}
Expected result: {expected_result}

Structural details of the target file:
{static_context}

Drafted test:
{drafted_code}

Pytest output (stdout/stderr tail):
{run_output}

Set is_test_code_bug to true only if rewriting the TEST would fix this, with a
concise suggested_fix describing what to change. Set it to false if the test
looks correct and the source code itself doesn't meet the scenario's expected
result -- in that case leave suggested_fix null. Explain your reasoning either way.
"""

prompt_template = PromptTemplate.from_template(CLASSIFY_FAILURE_PROMPT)


def classify_failure(state: CodeTestWriterState, runtime: Runtime[CodeTestWriterContext]) -> dict:
    scenario = runtime.context.scenarios[state.scenario_idx]
    llm = runtime.context.llm
    run_result = state.run_result

    run_output = ""
    if run_result is not None:
        run_output = (run_result.stdout + "\n" + run_result.stderr)[-MAX_OUTPUT_CHARS:]
        if run_result.timed_out:
            run_output += "\n[the test run timed out]"

    chain = prompt_template | llm.with_structured_output(FailureClassification)
    result = invoke_structured(chain, {
        "title": scenario.title,
        "description": scenario.description,
        "expected_result": scenario.expected_result,
        "static_context": state.static_context or "No structural details available",
        "drafted_code": state.drafted_code or "",
        "run_output": run_output,
    }, FailureClassification)

    attempts_exhausted = state.attempt >= runtime.context.max_attempts

    return {
        "classification": result,
        "attempts_exhausted": attempts_exhausted,
        "notes": result.reasoning,
    }


ROUTE_AFTER_CLASSIFICATION_T = Literal["retry_draft", "finalize"]


def route_after_classification(state: CodeTestWriterState) -> ROUTE_AFTER_CLASSIFICATION_T:
    if state.classification is not None and state.classification.is_test_code_bug and not state.attempts_exhausted:
        return "retry_draft"
    return "finalize"
