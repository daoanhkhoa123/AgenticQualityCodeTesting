from pathlib import Path

def read_file(path: str | Path) -> str:
    """
    Given a path, read markdown file and return as string
    """
    return Path(path).read_text(encoding="utf-8")

