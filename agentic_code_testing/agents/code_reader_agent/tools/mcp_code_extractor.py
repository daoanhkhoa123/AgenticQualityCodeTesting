import logging
from pathlib import Path
from typing import Any

from langchain_core.tools import BaseTool, StructuredTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from agentic_code_testing.agents.code_reader_agent.tools.path_safety import resolve_within_root

logger = logging.getLogger(__name__)

CODE_EXTRACTOR_SERVER_DIR = (
    Path(__file__).resolve().parents[4] / "third_party" / "mcp_servers" / "mcp_server_code_extractor"
)

# Name of the path/scope argument on each tool exposed by the code-extractor MCP
# server, so it can be routed through resolve_within_root before the call goes out.
# Only tools listed here are surfaced to the agent -- anything else the server adds
# in the future is skipped rather than exposed unsandboxed.
_PATH_ARG_BY_TOOL = {
    "get_symbols_tool": "path_or_url",
    "get_function_tool": "path_or_url",
    "get_class_tool": "path_or_url",
    "get_lines_tool": "path_or_url",
    "get_signature_tool": "path_or_url",
    "search_code_tool": "scope",
}


def _sandbox_path_arg(root_dir: Path, tool: BaseTool, path_arg: str) -> BaseTool:
    """Wrap an MCP code-extractor tool so its path/scope argument is confined to root_dir.

    The upstream server has no sandboxing of its own -- every tool takes a bare
    path_or_url/scope string and will fetch URLs or read anywhere the server
    process can see (it's explicitly designed to fetch GitHub/GitLab URLs). That
    would break the "read-only under root_dir" guarantee the rest of this agent
    enforces via resolve_within_root, so every call is routed through the same
    check here before it reaches the server.
    """

    async def sandboxed(**kwargs: Any) -> Any:
        raw = kwargs.get(path_arg)
        if not isinstance(raw, str) or not raw:
            raise ValueError(f"'{path_arg}' is required and must be a non-empty string.")
        if "://" in raw or raw.startswith("git@"):
            raise ValueError(
                f"'{path_arg}' must be a path under the project root, not a URL or remote ref."
            )
        resolved = resolve_within_root(root_dir, raw)
        kwargs[path_arg] = str(resolved)
        if tool.name == "search_code_tool":
            # The schema allows follow_symlinks=True, which could point outside
            # root_dir even though `scope` itself resolved inside it.
            kwargs["follow_symlinks"] = False
        return await tool.ainvoke(kwargs)

    return StructuredTool(
        name=tool.name,
        description=tool.description,
        args_schema=tool.args_schema,
        coroutine=sandboxed,
    )


async def make_mcp_code_extractor_tools(root_dir: Path) -> list[BaseTool]:
    """Connect to the mcp_server_code_extractor MCP server and return its tools,
    each sandboxed to root_dir.

    The server is launched as its own `uv run` subprocess from its vendored
    directory under third_party/, so it manages its own isolated venv (it needs
    Python >=3.11, independent of this project's requirement).
    """
    client = MultiServerMCPClient(
        {
            "code-extractor": {
                "command": "uv",
                "args": ["run", "--directory", str(CODE_EXTRACTOR_SERVER_DIR), "mcp-server-code-extractor"],
                "transport": "stdio",
            }
        }
    )
    tools = await client.get_tools()

    wrapped: list[BaseTool] = []
    for tool in tools:
        path_arg = _PATH_ARG_BY_TOOL.get(tool.name)
        if path_arg is None:
            logger.warning("Skipping unrecognized code-extractor MCP tool: %s", tool.name)
            continue
        wrapped.append(_sandbox_path_arg(root_dir, tool, path_arg))
    return wrapped
