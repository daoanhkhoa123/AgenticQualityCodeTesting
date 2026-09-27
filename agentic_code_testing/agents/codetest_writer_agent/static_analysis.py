import ast
import re
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from agentic_code_testing.agents.code_reader_agent.tools.path_safety import resolve_within_root

MAX_RELATED_TEST_FILES = 5

# Matches a relative-looking path ending in .py, e.g. "src/app.py" or "agents/foo/bar.py",
# as it might appear inline in a code_reader_agent free-text answer.
_PY_PATH_RE = re.compile(r"[\w./\\-]+\.py")


class FunctionInfo(BaseModel):
    name: str
    signature: str
    docstring: Optional[str] = None
    lineno: int


class ClassInfo(BaseModel):
    name: str
    methods: list[str] = Field(default_factory=list)
    docstring: Optional[str] = None
    lineno: int


class ModuleInfo(BaseModel):
    file_path: str
    imports: list[str] = Field(default_factory=list)
    functions: list[FunctionInfo] = Field(default_factory=list)
    classes: list[ClassInfo] = Field(default_factory=list)


def _render_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    return f"{prefix} {node.name}({ast.unparse(node.args)})"


def extract_module_info(source: str, file_path: str) -> ModuleInfo:
    """Parse `source` (the text of `file_path`) into a compact structural summary.

    Only top-level functions/classes/imports are collected -- enough to ground an
    LLM's test draft in real signatures and docstrings without dumping the whole
    file into the prompt.
    """
    tree = ast.parse(source, filename=file_path)

    imports: list[str] = []
    functions: list[FunctionInfo] = []
    classes: list[ClassInfo] = []

    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.extend(f"{module}.{alias.name}" if module else alias.name for alias in node.names)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(FunctionInfo(
                name=node.name,
                signature=_render_signature(node),
                docstring=ast.get_docstring(node),
                lineno=node.lineno,
            ))
        elif isinstance(node, ast.ClassDef):
            methods = [
                n.name for n in node.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            classes.append(ClassInfo(
                name=node.name,
                methods=methods,
                docstring=ast.get_docstring(node),
                lineno=node.lineno,
            ))

    return ModuleInfo(file_path=file_path, imports=imports, functions=functions, classes=classes)


def render_module_info(info: ModuleInfo) -> str:
    """Compact text block suitable for injecting into an LLM prompt."""
    lines = [f"File: {info.file_path}"]

    if info.imports:
        lines.append("Imports: " + ", ".join(info.imports))

    for fn in info.functions:
        lines.append(f"- {fn.signature}")
        if fn.docstring:
            lines.append(f"    {fn.docstring}")

    for cls in info.classes:
        lines.append(f"- class {cls.name}({', '.join(cls.methods)})")
        if cls.docstring:
            lines.append(f"    {cls.docstring}")

    return "\n".join(lines)


def find_related_test_files(root_dir: Path, module_relpath: str) -> list[Path]:
    """Heuristic lookup of existing test files that might already cover/target
    the same module, so a draft can reuse their fixtures instead of duplicating
    setup. Best-effort: a few common naming conventions, capped, not a full
    fixture-dependency resolver.
    """
    module_path = Path(module_relpath)
    stem = module_path.stem
    candidates: list[Path] = []

    for pattern in (f"test_{stem}.py", f"{stem}_test.py"):
        candidates.extend(root_dir.rglob(pattern))

    tests_dir = module_path.parent / "tests"
    resolved_tests_dir = (root_dir / tests_dir)
    if resolved_tests_dir.is_dir():
        candidates.extend(p for p in resolved_tests_dir.glob("*.py") if p.name != "__init__.py")

    seen: set[Path] = set()
    unique: list[Path] = []
    for path in candidates:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)

    return unique[:MAX_RELATED_TEST_FILES]


def extract_file_path_from_answer(answer: str, root_dir: Path) -> Optional[str]:
    """Scan a code_reader_agent free-text answer for a `.py` path it mentioned,
    returning the first one that resolves to a real file inside root_dir.

    Scenario objects carry no explicit target-file field, so this is the glue
    that turns a Q&A answer back into something static_analysis can open. Best
    effort: returns None if nothing in the answer resolves to a real file.
    """
    for match in _PY_PATH_RE.finditer(answer):
        candidate = match.group(0).strip("`'\" ").replace("\\", "/")
        try:
            resolved = resolve_within_root(root_dir, candidate)
        except ValueError:
            continue
        if resolved.is_file():
            return str(resolved.relative_to(root_dir.resolve()))
    return None
