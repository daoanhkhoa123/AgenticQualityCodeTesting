from agentic_code_testing.agents.codetest_writer_agent.pytest_runner import (
    clear_stale_scratch,
    run_pytest_on_code,
)

SCRATCH_DIR_NAME = ".codetest_writer_scratch"


def _scratch_dir(root_dir, scenario_id, attempt):
    return root_dir / SCRATCH_DIR_NAME / scenario_id / f"attempt_{attempt}"


def test_run_pytest_on_code_passing_test_returns_zero(tmp_path):
    code = "def test_ok():\n    assert True\n"

    result = run_pytest_on_code(code, "passing-scenario", 0, tmp_path, SCRATCH_DIR_NAME, timeout=30)

    assert result.returncode == 0
    assert not result.timed_out
    assert not _scratch_dir(tmp_path, "passing-scenario", 0).exists()


def test_run_pytest_on_code_failing_test_returns_nonzero_with_failure_text(tmp_path):
    code = "def test_fail():\n    assert False, 'deliberate failure'\n"

    result = run_pytest_on_code(code, "failing-scenario", 0, tmp_path, SCRATCH_DIR_NAME, timeout=30)

    assert result.returncode != 0
    assert not result.timed_out
    assert "deliberate failure" in result.stdout
    assert not _scratch_dir(tmp_path, "failing-scenario", 0).exists()


def test_run_pytest_on_code_times_out(tmp_path):
    code = "import time\n\ndef test_slow():\n    time.sleep(10)\n"

    result = run_pytest_on_code(code, "slow-scenario", 0, tmp_path, SCRATCH_DIR_NAME, timeout=2)

    assert result.timed_out
    assert not _scratch_dir(tmp_path, "slow-scenario", 0).exists()


def test_clear_stale_scratch_removes_leftover_directory(tmp_path):
    stale = tmp_path / SCRATCH_DIR_NAME / "some-scenario" / "attempt_0"
    stale.mkdir(parents=True)
    (stale / "test_some-scenario.py").write_text("def test_x(): pass\n", encoding="utf-8")

    clear_stale_scratch(tmp_path, SCRATCH_DIR_NAME)

    assert not (tmp_path / SCRATCH_DIR_NAME).exists()
