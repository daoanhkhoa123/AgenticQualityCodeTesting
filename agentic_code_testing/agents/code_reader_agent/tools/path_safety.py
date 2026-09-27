from pathlib import Path


def resolve_within_root(root_dir: Path, relative: str) -> Path:
    """Resolve `relative` against `root_dir` and reject anything that escapes it.

    Raises ValueError if the resolved path is outside root_dir, so a tool-calling
    agent sees a clear error message instead of being able to read/list arbitrary
    filesystem paths.
    """
    candidate = (root_dir / relative).resolve()
    if not candidate.is_relative_to(root_dir):
        raise ValueError(
            f"Path '{relative}' resolves outside the allowed root directory "
            f"'{root_dir}'. Only paths inside the given project directory can be accessed."
        )
    return candidate
