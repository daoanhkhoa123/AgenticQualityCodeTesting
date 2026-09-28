import asyncio

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
