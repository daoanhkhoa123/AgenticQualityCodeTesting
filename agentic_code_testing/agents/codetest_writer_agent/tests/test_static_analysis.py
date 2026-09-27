from agentic_code_testing.agents.codetest_writer_agent.utils.static_analysis import (
    extract_file_path_from_answer,
    extract_module_info,
    find_related_test_files,
)
from agentic_code_testing.agents.codetest_writer_agent.tests.mock_data import FIXTURE_DIR, MATHY_PATH


def test_extract_module_info_finds_functions_with_signatures_and_docstrings():
    source = MATHY_PATH.read_text(encoding="utf-8")
    info = extract_module_info(source, "mathy.py")

    names = {fn.name for fn in info.functions}
    assert names == {"add", "is_even"}

    add_fn = next(fn for fn in info.functions if fn.name == "add")
    assert "a: int" in add_fn.signature
    assert "b: int" in add_fn.signature
    assert add_fn.docstring == "Return the sum of a and b."

    is_even_fn = next(fn for fn in info.functions if fn.name == "is_even")
    assert is_even_fn.docstring == "Return True if n is even."


def test_extract_file_path_from_answer_finds_real_path():
    answer = "The function is defined in mathy.py, specifically the add function."
    path = extract_file_path_from_answer(answer, FIXTURE_DIR)
    assert path == "mathy.py"


def test_extract_file_path_from_answer_returns_none_for_nonexistent_file():
    answer = "This is defined in nonexistent_module.py somewhere."
    assert extract_file_path_from_answer(answer, FIXTURE_DIR) is None


def test_extract_file_path_from_answer_rejects_path_escape():
    answer = "See ../../../etc/passwd.py for details."
    assert extract_file_path_from_answer(answer, FIXTURE_DIR) is None


def test_find_related_test_files_matches_conventional_names(tmp_path):
    (tmp_path / "mathy.py").write_text("def add(a, b): return a + b\n", encoding="utf-8")
    (tmp_path / "test_mathy.py").write_text("def test_add(): pass\n", encoding="utf-8")

    related = find_related_test_files(tmp_path, "mathy.py")

    assert any(path.name == "test_mathy.py" for path in related)
