import logging
from pathlib import Path

from langchain.agents import create_agent
from langchain_core.language_models.chat_models import BaseChatModel

from agentic_code_testing.agents.code_reader_agent.tools.list_directory import make_list_directory_tool
from agentic_code_testing.agents.code_reader_agent.tools.read_file import make_read_file_tool
from agentic_code_testing.agents.code_reader_agent.tools.search_in_files import make_search_in_files_tool
from agentic_code_testing.logging.pydantic_logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You answer questions about the code in a project directory. You can only list
directories, search files, and read file contents -- you cannot run anything.

- Explore first: list_directory, then search_in_files/read_file, before answering.
- Ground answers only in what you actually read here; cite file paths (and line
  numbers from search_in_files).
- If the files don't give you enough to answer, say so instead of guessing.
"""


def create_code_reader_agent(llm: BaseChatModel, root_dir: str | Path):
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
    ]
    return create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)

