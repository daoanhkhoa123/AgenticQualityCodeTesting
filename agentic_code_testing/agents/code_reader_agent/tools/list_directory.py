from pathlib import Path

from langchain.tools import tool

from agentic_code_testing.agents.code_reader_agent.tools.path_safety import resolve_within_root

DEFAULT_IGNORE = {
    ".git", "__pycache__", ".venv", "venv", "node_modules",
    ".mypy_cache", ".pytest_cache", ".idea", ".vscode", "dist", "build", ".egg-info",
}


def _display_path(item: Path, display_root: Path) -> str:
    """Path shown to the LLM: relative to display_root, so it's directly usable
    as the `path` argument to read_file/search_in_files."""
    resolved = item.resolve()
    try:
        return str(resolved.relative_to(display_root.resolve()))
    except ValueError:
        return str(resolved)


def print_tree(directory, depth=None, current_depth=0, prefix="", ignore=None, display_root=None) -> str:
    """Build a directory tree as a string.

    Args:
        directory: Root directory to scan.
        depth: Maximum depth to traverse. None means unlimited.
        current_depth: Internal recursion depth.
        prefix: Internal tree prefix formatting.
        ignore: Optional set of file/folder names to skip entirely.
        display_root: Directory that shown paths are made relative to. Defaults
            to `directory` itself.

    Returns:
        A string representation of the directory tree.
    """
    dir_path = Path(directory)
    display_root = Path(display_root) if display_root is not None else dir_path
    lines = []

    if depth is not None and current_depth > depth:
        return ""

    if current_depth == 0:
        lines.append(f"[Folder] {_display_path(dir_path, display_root) or '.'}")

    try:
        items = [item for item in dir_path.iterdir() if not ignore or item.name not in ignore]
    except PermissionError:
        lines.append(f"{prefix}└── [Permission Denied]")
        return "\n".join(lines)

    items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))

    for index, item in enumerate(items):
        is_last = index == len(items) - 1
        connector = "└── " if is_last else "├── "
        icon = "[Folder]" if item.is_dir() else "[File]"
        item_path = _display_path(item, display_root)
        lines.append(f"{prefix}{connector}{icon} {item.name} ({item_path})")

        if item.is_dir():
            child_prefix = prefix + ("    " if is_last else "│   ")
            child_tree = print_tree(
                item,
                depth=depth,
                current_depth=current_depth + 1,
                prefix=child_prefix,
                ignore=ignore,
                display_root=display_root,
            )
            if child_tree:
                lines.append(child_tree)

    return "\n".join(lines)


def make_list_directory_tool(root_dir: Path):
    @tool
    def list_directory(subdirectory: str = ".", depth: int | None = None) -> str:
        """List files and folders under a directory as an ASCII tree.

        Use this first to orient yourself before reading or searching files.
        Common noise directories (.git, __pycache__, .venv, node_modules, etc.)
        are hidden automatically. Paths shown in parentheses are relative to the
        project root -- pass them as-is to read_file/search_in_files.

        Args:
            subdirectory: Path relative to the project root to list. Use "." for
                the project root itself.
            depth: Maximum recursion depth. Omit for the full tree.
        """
        target = resolve_within_root(root_dir, subdirectory)
        return print_tree(target, depth=depth, ignore=DEFAULT_IGNORE, display_root=root_dir)

    return list_directory
