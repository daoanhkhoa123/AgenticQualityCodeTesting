import subprocess
import sys

from agentic_code_testing.agents.codetest_writer_agent.utils.pytest_runner import (
    _detect_venv_python,
    clear_stale_scratch,
    run_pytest_on_code,
)

SCRATCH_DIR_NAME = ".codetest_writer_scratch"


def _scratch_dir(root_dir, scenario_id, attempt):
    return root_dir / SCRATCH_DIR_NAME / scenario_id / f"attempt_{attempt}"


def _make_windows_venv_python(root_dir):
    python_path = root_dir / ".venv" / "Scripts" / "python.exe"
    python_path.parent.mkdir(parents=True)
    python_path.touch()
    return python_path


def _make_posix_venv_python(root_dir):
    python_path = root_dir / ".venv" / "bin" / "python"
    python_path.parent.mkdir(parents=True)
    python_path.touch()
    return python_path


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


def test_detect_venv_python_finds_windows_layout(tmp_path):
    python_path = _make_windows_venv_python(tmp_path)

    assert _detect_venv_python(tmp_path) == python_path


def test_detect_venv_python_finds_posix_layout(tmp_path):
    python_path = _make_posix_venv_python(tmp_path)

    assert _detect_venv_python(tmp_path) == python_path


def test_detect_venv_python_returns_none_when_no_venv(tmp_path):
    assert _detect_venv_python(tmp_path) is None


def test_run_pytest_on_code_uses_detected_venv_python(tmp_path, monkeypatch):
    venv_python = (
        _make_windows_venv_python(tmp_path) if sys.platform == "win32" else _make_posix_venv_python(tmp_path)
    )
    captured = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        return subprocess.CompletedProcess(argv, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(
        "agentic_code_testing.agents.codetest_writer_agent.utils.pytest_runner.subprocess.run", fake_run
    )

    run_pytest_on_code("def test_ok():\n    assert True\n", "venv-scenario", 0, tmp_path, SCRATCH_DIR_NAME, timeout=30)

    assert captured["argv"][0] == str(venv_python)


def test_run_pytest_on_code_falls_back_to_sys_executable_without_venv(tmp_path, monkeypatch):
    captured = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        return subprocess.CompletedProcess(argv, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(
        "agentic_code_testing.agents.codetest_writer_agent.utils.pytest_runner.subprocess.run", fake_run
    )

    run_pytest_on_code("def test_ok():\n    assert True\n", "no-venv-scenario", 0, tmp_path, SCRATCH_DIR_NAME, timeout=30)

    assert captured["argv"][0] == sys.executable
