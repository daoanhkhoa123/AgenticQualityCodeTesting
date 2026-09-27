import shutil
import subprocess
import sys
from pathlib import Path

from agentic_code_testing.agents.code_reader_agent.tools.path_safety import resolve_within_root
from agentic_code_testing.agents.codetest_writer_agent.typed_schemas import TestRunResult


def run_pytest_on_code(
    code: str,
    scenario_id: str,
    attempt: int,
    root_dir: Path,
    scratch_dir_name: str,
    timeout: float = 60.0,
) -> TestRunResult:
    """Write `code` as a pytest file into a scratch dir under root_dir and run it.

    The scratch dir lives inside root_dir (not a fully separate tempfile.mkdtemp())
    so pytest's normal upward discovery of the target project's own conftest.py /
    pytest.ini / fixtures still works -- a file outside the tree wouldn't see any
    of that. It is always removed afterwards, pass or fail or timeout.
    """
    scratch_dir = resolve_within_root(root_dir, f"{scratch_dir_name}/{scenario_id}/attempt_{attempt}")
    scratch_dir.mkdir(parents=True, exist_ok=True)
    test_path = scratch_dir / f"test_{scenario_id}.py"
    test_path.write_text(code, encoding="utf-8")

    python_executable = _detect_venv_python(root_dir) or Path(sys.executable)

    try:
        completed = subprocess.run(
            [str(python_executable), "-m", "pytest", str(test_path), "--tb=short", "-q"],
            cwd=str(root_dir),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return TestRunResult(
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            timed_out=False,
        )
    except subprocess.TimeoutExpired as exc:
        return TestRunResult(
            returncode=-1,
            stdout=(exc.stdout or b"").decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or ""),
            stderr=(exc.stderr or b"").decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or ""),
            timed_out=True,
        )
    finally:
        shutil.rmtree(scratch_dir, ignore_errors=True)
        _remove_empty_parents(scratch_dir.parent, stop_at=root_dir)


def _detect_venv_python(root_dir: Path) -> Path | None:
    """Return the python executable of a uv-managed venv at root_dir/.venv, if present.

    Checks both the Windows and POSIX layouts unconditionally rather than
    branching on os.name/sys.platform first -- uv only ever creates one of
    these depending on the OS it ran on, so at most one candidate exists, and
    checking both keeps the function portable and testable on any host OS.
    """
    for candidate in (
        root_dir / ".venv" / "Scripts" / "python.exe",
        root_dir / ".venv" / "bin" / "python",
    ):
        if candidate.is_file():
            return candidate
    return None


def _remove_empty_parents(directory: Path, stop_at: Path) -> None:
    """Remove `directory` and any now-empty ancestors, stopping at (and not
    removing) `stop_at`. Keeps run_pytest_on_code from leaving behind the
    empty per-scenario/scratch-root directories after its own leaf cleanup."""
    current = directory
    while current != stop_at and current.is_dir() and not any(current.iterdir()):
        current.rmdir()
        current = current.parent


def clear_stale_scratch(root_dir: Path, scratch_dir_name: str) -> None:
    """Remove any leftover scratch directory from a previous run that crashed
    before its own cleanup ran. Safe to call unconditionally at startup."""
    stale = root_dir / scratch_dir_name
    shutil.rmtree(stale, ignore_errors=True)
