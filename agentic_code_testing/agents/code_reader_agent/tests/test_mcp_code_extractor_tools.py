import asyncio

import pytest

from agentic_code_testing.agents.code_reader_agent.tests.mock_data import FIXTURE_DIR
from agentic_code_testing.agents.code_reader_agent.tools.mcp_code_extractor import make_mcp_code_extractor_tools


def _make_tools():
    return asyncio.run(make_mcp_code_extractor_tools(FIXTURE_DIR))


def _get_tool(tools, name):
    return next(t for t in tools if t.name == name)


def test_exposes_expected_tool_names():
    tools = _make_tools()
    names = {t.name for t in tools}
    assert names == {
        "get_symbols_tool",
        "get_function_tool",
        "get_class_tool",
        "get_lines_tool",
        "get_signature_tool",
        "search_code_tool",
    }


def test_get_symbols_tool_finds_real_symbol():
    tools = _make_tools()
    get_symbols = _get_tool(tools, "get_symbols_tool")

    result = asyncio.run(get_symbols.ainvoke({"path_or_url": "read_file.py"}))

    assert "read_file" in str(result)


def test_rejects_url_path():
    tools = _make_tools()
    get_symbols = _get_tool(tools, "get_symbols_tool")

    with pytest.raises(ValueError):
        asyncio.run(get_symbols.ainvoke({"path_or_url": "https://example.com/read_file.py"}))


def test_rejects_path_escaping_root():
    tools = _make_tools()
    get_symbols = _get_tool(tools, "get_symbols_tool")

    with pytest.raises(ValueError):
        asyncio.run(get_symbols.ainvoke({"path_or_url": "../../../../etc/passwd"}))


def test_search_code_tool_ignores_follow_symlinks_override():
    tools = _make_tools()
    search_code = _get_tool(tools, "search_code_tool")

    result = asyncio.run(search_code.ainvoke({
        "search_type": "symbol-definitions",
        "target": "read_file",
        "scope": ".",
        "follow_symlinks": True,
    }))

    assert result is not None
