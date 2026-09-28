from pathlib import Path


def resolve_within_root(root_dir: Path, relative: str) -> Path:
    """Resolve `relative` against `root_dir` and reject anything that escapes it.

    Raises ValueError if the resolved path is outside root_dir. Every caller
    exposed as a tool must catch this and return the message as a string --
    never let it propagate -- or a bad/malicious path from the LLM crashes the
    whole agent run instead of giving the model a normal, recoverable answer.
    """
    candidate = (root_dir / relative).resolve()
    if not candidate.is_relative_to(root_dir):
        raise ValueError(
            f"Path '{relative}' resolves outside the allowed root directory "
            f"'{root_dir}'. Only paths inside the given project directory can be accessed."
        )
    return candidate
