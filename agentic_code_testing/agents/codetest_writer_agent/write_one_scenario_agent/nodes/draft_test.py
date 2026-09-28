from typing import Literal

from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from agentic_code_testing.agents.codetest_writer_agent.utils.structured_output import invoke_structured
from agentic_code_testing.agents.codetest_writer_agent.typed_schemas import (
    CodeTestWriterContext,
    CodeTestWriterState,
    DraftedTest,
)

MAX_FEEDBACK_CHARS = 4_000

DRAFT_TEST_PROMPT = """
Write a single pytest test file for this scenario:

Title: {title}
Category: {category}
Description: {description}
Preconditions: {preconditions}
Steps:
{steps}
Expected result: {expected_result}

Code context from reading the target project:
{code_context}

Structural details of the target file (signatures, docstrings, existing tests to reuse):
{static_context}

{retry_context}

Return the complete test file source, including all needed imports. The file
must be self-contained and runnable with `pytest` as-is.

If the code context above is missing or insufficient to draft a test grounded
in the real implementation, do NOT guess: leave code null and set
code_context_question to a specific question about the codebase you need
answered first. Otherwise leave code_context_question null.
"""

prompt_template = PromptTemplate.from_template(DRAFT_TEST_PROMPT)


def _render_retry_context(state: CodeTestWriterState) -> str:
    if state.attempt == 0 or state.drafted_code is None:
        return ""

    feedback_lines = [
        "A previous attempt at this test failed. Here is what was tried and why it failed --",
        "fix the problem instead of repeating it.",
        "",
        "Previous drafted test:",
        state.drafted_code,
    ]

    if state.run_result is not None:
        tail = (state.run_result.stdout + "\n" + state.run_result.stderr)[-MAX_FEEDBACK_CHARS:]
        feedback_lines += ["", "Pytest output from that attempt:", tail]

    if state.classification is not None and state.classification.suggested_fix:
        feedback_lines += ["", "Suggested fix:", state.classification.suggested_fix]

    return "\n".join(feedback_lines)


def draft_test(state: CodeTestWriterState, runtime: Runtime[CodeTestWriterContext]) -> dict:
    scenario = runtime.context.scenarios[state.scenario_idx]
    llm = runtime.context.llm

    # method="json_schema" (rather than the default tool-calling method) is more
    # reliable here: a full source-code string field tends to make this model
    # answer in prose with markdown fences instead of invoking a tool call.
    chain = prompt_template | llm.with_structured_output(DraftedTest, method="json_schema")
    result = invoke_structured(chain, {
        "title": scenario.title,
        "category": scenario.category,
        "description": scenario.description,
        "preconditions": scenario.preconditions or "None",
        "steps": "\n".join(f"- {step}" for step in scenario.steps) or "None",
        "expected_result": scenario.expected_result,
        "code_context": state.code_context or "No code context available",
        "static_context": state.static_context or "No structural details available",
        "retry_context": _render_retry_context(state),
    }, DraftedTest)

    question = (result.code_context_question or "").strip()
    if question:
        return {"pending_code_context_question": question}

    if not result.code:
        # Model returned neither code nor a question -- ask a generic fallback
        # instead of letting an empty draft reach run_drafted_test.
        return {"pending_code_context_question": "What file and function/class does this scenario need a test for?"}

    return {
        "drafted_code": result.code,
        "attempt": state.attempt + 1,
        "notes": result.rationale or "",
    }


ROUTE_AFTER_DRAFT_T = Literal["needs_context", "run_test"]


def route_after_draft(state: CodeTestWriterState) -> ROUTE_AFTER_DRAFT_T:
    if state.pending_code_context_question:
        return "needs_context"
    return "run_test"
