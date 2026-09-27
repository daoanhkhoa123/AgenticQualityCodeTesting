from agentic_code_testing.agents.codetest_writer_agent.guardrails import find_violations
from agentic_code_testing.agents.codetest_writer_agent.typed_schemas import (
    CodeTestWriterState,
    TestRunResult,
)
from agentic_code_testing.agents.codetest_writer_agent.write_one_scenario_agent.nodes.finalize import finalize
from agentic_code_testing.agents.codetest_writer_agent.write_one_scenario_agent.nodes.run_drafted_test import (
    route_after_run,
    run_drafted_test,
)

CLEAN_CODE = """
import pytest

from mathy import add


def test_add_returns_sum():
    assert add(2, 3) == 5
"""


def test_find_violations_returns_empty_for_clean_code():
    assert find_violations(CLEAN_CODE) == []


def test_find_violations_returns_empty_for_missing_code():
    assert find_violations(None) == []


def test_find_violations_catches_filesystem_destruction():
    code = "import shutil\nshutil.rmtree('/some/dir')\n"
    violations = find_violations(code)
    assert any("rmtree" in v for v in violations)


def test_find_violations_catches_network_access():
    code = "import requests\n\ndef test_x():\n    requests.get('http://example.com')\n"
    violations = find_violations(code)
    assert any("requests" in v for v in violations)


def test_find_violations_catches_process_execution():
    code = "import subprocess\nsubprocess.run(['echo', 'hi'])\n"
    violations = find_violations(code)
    assert any("subprocess" in v for v in violations)


def test_find_violations_catches_dynamic_code_execution():
    code = "def test_x():\n    eval('1 + 1')\n"
    violations = find_violations(code)
    assert any("eval" in v for v in violations)


def test_find_violations_is_case_insensitive():
    code = "import REQUESTS\n"
    assert find_violations(code) != []


def test_run_drafted_test_skips_execution_when_blocked():
    state = CodeTestWriterState(
        scenario_idx=0,
        drafted_code="import os\n\ndef test_x():\n    os.remove('some_file.txt')\n",
    )

    result = run_drafted_test(state, runtime=None)

    assert "blocked_reasons" in result
    assert result["blocked_reasons"]
    assert "run_result" not in result


def test_route_after_run_finalizes_when_blocked_regardless_of_stale_run_result():
    state = CodeTestWriterState(
        scenario_idx=0,
        blocked_reasons=["os.remove (deletes a file)"],
        run_result=TestRunResult(returncode=0, stdout="", stderr=""),
    )
    assert route_after_run(state) == "finalize"


def test_route_after_run_finalizes_on_pass():
    state = CodeTestWriterState(scenario_idx=0, run_result=TestRunResult(returncode=0, stdout="", stderr=""))
    assert route_after_run(state) == "finalize"


def test_route_after_run_classifies_on_failure():
    state = CodeTestWriterState(scenario_idx=0, run_result=TestRunResult(returncode=1, stdout="", stderr=""))
    assert route_after_run(state) == "classify_failure"


def test_finalize_reports_blocked_status_with_reasons():
    state = CodeTestWriterState(
        scenario_idx=0,
        attempt=1,
        blocked_reasons=["os.remove (deletes a file)", "subprocess (spawns processes)"],
    )

    result = finalize(state)

    assert result["status"] == "blocked"
    assert "os.remove" in result["notes"]
    assert "subprocess" in result["notes"]
