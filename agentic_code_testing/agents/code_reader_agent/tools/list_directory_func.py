from pathlib import Path


def print_tree(directory, depth=None, current_depth=0, prefix="") -> str:
    """Build a directory tree as a string.

    Args:
        directory: Root directory to scan.
        depth: Maximum depth to traverse. None means unlimited.
        current_depth: Internal recursion depth.
        prefix: Internal tree prefix formatting.

    Returns:
        A string representation of the directory tree.
    """
    dir_path = Path(directory)
    lines = []

    if depth is not None and current_depth > depth:
        return ""

    if current_depth == 0:
        root_display = str(dir_path.resolve())
        lines.append(f"[Folder] {root_display}")

    try:
        items = list(dir_path.iterdir())
    except PermissionError:
        lines.append(f"{prefix}└── [Permission Denied]")
        return "\n".join(lines)

    items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))

    for index, item in enumerate(items):
        is_last = index == len(items) - 1
        connector = "└── " if is_last else "├── "
        icon = "[Folder]" if item.is_dir() else "[File]"
        item_path = str(item.resolve())
        lines.append(f"{prefix}{connector}{icon} {item.name} ({item_path})")

        if item.is_dir():
            child_prefix = prefix + ("    " if is_last else "│   ")
            child_tree = print_tree(
                item,
                depth=depth,
                current_depth=current_depth + 1,
                prefix=child_prefix,
            )
            if child_tree:
                lines.append(child_tree)

    return "\n".join(lines)
