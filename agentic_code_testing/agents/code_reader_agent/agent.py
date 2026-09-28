import logging
from pathlib import Path

from langchain.agents import create_agent
from langchain_core.language_models.chat_models import BaseChatModel

from agentic_code_testing.agents.code_reader_agent.tools.list_directory import make_list_directory_tool
from agentic_code_testing.agents.code_reader_agent.tools.mcp_code_extractor import make_mcp_code_extractor_tools
from agentic_code_testing.agents.code_reader_agent.tools.read_file import make_read_file_tool
from agentic_code_testing.agents.code_reader_agent.tools.search_in_files import make_search_in_files_tool
from agentic_code_testing.logging.pydantic_logger import setup_logging
from agentic_code_testing.tracing.config import configure_tracing

setup_logging()
configure_tracing()
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You answer questions about the code in a project directory. You can only list
directories, search files, and read file/symbol contents -- you cannot run anything.

- Explore first: list_directory for the tree, search_code_tool/search_in_files to find
  relevant files or symbols by name before you know a specific file path.
- get_symbols_tool/get_function_tool/get_class_tool/get_signature_tool/get_lines_tool
  all require an already-known file path (from list_directory/search_code_tool/
  search_in_files) -- never call them before you have one.
- Once you know what you're looking for, get_function_tool/get_class_tool/
  get_signature_tool pull the exact definition; get_lines_tool/read_file/
  search_in_files cover exact line ranges, plain-text files, or anything the
  symbol tools don't apply to (e.g. non-code files).
- Ground answers only in what you actually read here; cite file paths (and line
  numbers from search_in_files/get_lines_tool).
- If the files don't give you enough to answer, say so instead of guessing.
"""


async def create_code_reader_agent(llm: BaseChatModel, root_dir: str | Path):
    """Build a ReAct agent scoped to read-only access under root_dir.

    root_dir is fixed at build time, not exposed as a tool argument -- it is the
    security boundary the tools enforce, so it must be set by the trusted caller,
    never by the LLM. If this agent is hosted for other agents to query and the
    target directory changes per request, call this factory again for each
    request with that request's root_dir, then invoke the returned agent.
    """
    root = Path(root_dir).resolve()
    tools = [
        make_list_directory_tool(root),
        make_read_file_tool(root),
        make_search_in_files_tool(root),
        *await make_mcp_code_extractor_tools(root),
    ]
    return create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)

