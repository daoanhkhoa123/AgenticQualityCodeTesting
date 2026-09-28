import re
from pathlib import Path

from langchain.tools import tool

from agentic_code_testing.agents.code_reader_agent.tools.list_directory import DEFAULT_IGNORE
from agentic_code_testing.agents.code_reader_agent.tools.path_safety import resolve_within_root

MAX_MATCHES = 200


def make_search_in_files_tool(root_dir: Path):
    @tool
    def search_in_files(pattern: str, subdirectory: str = ".") -> str:
        """Search for a regex pattern across text files under a directory.

        Use this to find where something is defined/used before reading whole
        files. Returns matching lines as "path:line: text", capped at 200 hits.

        Args:
            pattern: Regular expression to search for (case-insensitive).
            subdirectory: Path relative to the project root to search under.
        """
        try:
            target = resolve_within_root(root_dir, subdirectory)
        except ValueError as e:
            return f"Error: {e}"
        if not target.is_dir():
            return f"Error: '{subdirectory}' is not a directory (it may be a file or not exist)."
        regex = re.compile(pattern, re.IGNORECASE)
        hits: list[str] = []
        for file_path in target.rglob("*"):
            if not file_path.is_file() or any(part in DEFAULT_IGNORE for part in file_path.parts):
                continue
            try:
                text = file_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for line_no, line in enumerate(text.splitlines(), start=1):
                if regex.search(line):
                    hits.append(f"{file_path.resolve()}:{line_no}: {line.strip()}")
                    if len(hits) >= MAX_MATCHES:
                        break
            if len(hits) >= MAX_MATCHES:
                break
        return "\n".join(hits) if hits else "No matches found."

    return search_in_files
