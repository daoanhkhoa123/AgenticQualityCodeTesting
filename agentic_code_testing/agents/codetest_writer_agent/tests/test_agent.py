from langgraph.graph import StateGraph, START, END

from agentic_code_testing.agents.codetest_writer_agent.agent import invoke_codetest_writer_agent
from agentic_code_testing.agents.codetest_writer_agent.tests.mock_data import (
    FIXTURE_DIR,
    SCENARIO_ADD_HAPPY_PATH,
    SCENARIO_IS_EVEN_BUGGY,
)
from agentic_code_testing.agents.codetest_writer_agent.typed_schemas import (
    CodeTestWriterContext,
    CodeTestWriterState,
    TestRunResult,
)
from agentic_code_testing.agents.codetest_writer_agent.write_one_scenario_agent.nodes.classify_failure import (
    classify_failure,
)
from agentic_code_testing.agents.codetest_writer_agent.write_report.test_file_writer import GeneratedTestWriter
from agentic_code_testing.llm.groq_client import llm

MAX_ATTEMPTS = 3


def _safe_print(text: str) -> None:
    """print() that won't crash the test if the LLM's output contains a Unicode
    character the Windows console's codepage can't encode (e.g. typographic
    punctuation) -- the test's actual assertions matter more than raw display."""
    print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def test_invoke_codetest_writer_agent_drafts_a_passing_test_for_correct_function(tmp_path):
    results = invoke_codetest_writer_agent(
        llm, [SCENARIO_ADD_HAPPY_PATH], GeneratedTestWriter(), tmp_path,
        root_dir=str(FIXTURE_DIR), max_attempts=MAX_ATTEMPTS,
    )

    assert len(results) == 1
    result = results[0]
    _safe_print(f"result:\n{result}\n")

    assert result.attempts <= MAX_ATTEMPTS
    assert result.status == "passed"
    assert (tmp_path / f"test_{result.scenario_id}.py").exists()
    assert (tmp_path / "report.md").exists()


def test_invoke_codetest_writer_agent_flags_a_real_source_bug_instead_of_looping_forever(tmp_path):
    results = invoke_codetest_writer_agent(
        llm, [SCENARIO_IS_EVEN_BUGGY], GeneratedTestWriter(), tmp_path,
        root_dir=str(FIXTURE_DIR), max_attempts=MAX_ATTEMPTS,
    )

    assert len(results) == 1
    result = results[0]
    _safe_print(f"result:\n{result}\n")

    # Deterministic regardless of LLM phrasing: the loop must terminate within
    # max_attempts and must not report success against a genuinely buggy function.
    assert result.attempts <= MAX_ATTEMPTS
    assert result.status != "passed"

    # Soft check on classification quality -- printed for manual review since an
    # occasional misclassification is tolerated (see plan's Risks section).
    if result.status != "flagged_source_bug":
        _safe_print(f"NOTE: expected flagged_source_bug, got {result.status}. notes: {result.notes}")


def test_classify_failure_recognizes_an_obvious_test_code_bug():
    mini_builder = StateGraph(CodeTestWriterState, context_schema=CodeTestWriterContext)
    mini_builder.add_node("classify_failure", classify_failure)
    mini_builder.add_edge(START, "classify_failure")
    mini_builder.add_edge("classify_failure", END)
    mini_graph = mini_builder.compile()

    state = CodeTestWriterState(
        scenario_idx=0,
        attempt=1,
        drafted_code=(
            "import nonexistent_module_xyz\n\n"
            "def test_add():\n"
            "    assert nonexistent_module_xyz.add(2, 3) == 5\n"
        ),
        run_result=TestRunResult(
            returncode=1,
            stdout="ModuleNotFoundError: No module named 'nonexistent_module_xyz'",
            stderr="",
            timed_out=False,
        ),
    )
    context = CodeTestWriterContext(
        llm=llm, scenarios=[SCENARIO_ADD_HAPPY_PATH], root_dir=str(FIXTURE_DIR), max_attempts=MAX_ATTEMPTS,
    )

    result = mini_graph.invoke(state, context=context)
    _safe_print(f"classification:\n{result['classification']}\n")

    assert result["classification"].is_test_code_bug is True
