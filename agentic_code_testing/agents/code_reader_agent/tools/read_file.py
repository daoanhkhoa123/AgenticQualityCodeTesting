from pathlib import Path

from langchain.tools import tool

from agentic_code_testing.agents.code_reader_agent.tools.path_safety import resolve_within_root

MAX_CHARS = 20_000


def make_read_file_tool(root_dir: Path):
    @tool
    def read_file(path: str) -> str:
        """Read and return the text content of a single file.

        Args:
            path: File path relative to the project root (e.g. "src/app.py").

        Returns the file's full text (UTF-8, decode errors replaced), truncated
        with a notice if it exceeds a safe size limit. Only reports what the
        file actually contains -- never execute, run, or import the file.
        """
        target = resolve_within_root(root_dir, path)
        if not target.is_file():
            raise ValueError(f"'{path}' is not a file (it may be a directory or not exist).")
        text = target.read_text(encoding="utf-8", errors="replace")
        if len(text) > MAX_CHARS:
            return text[:MAX_CHARS] + f"\n...[truncated, {len(text)} chars total]"
        return text

    return read_file
