"""A2A client for calling this agent's server (see __main__.py / agent_executor.py)."""

import asyncio
import logging

from a2a.client import create_client
from a2a.helpers import get_stream_response_text, new_data_part, new_message, new_text_part
from a2a.types.a2a_pb2 import Role, SendMessageRequest

from agentic_code_testing.agents.code_reader_agent.config import ServerConfig

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = f"http://{ServerConfig.code_reader_agent_host}:{ServerConfig.code_reader_agent_port}"


async def ask_code_reader_async(question: str, root_dir: str, base_url: str = DEFAULT_BASE_URL) -> str:
    """Sends `question` to the code_reader_agent A2A server, scoped to `root_dir`."""
    client = await create_client(base_url)
    try:
        message = new_message(
            parts=[new_text_part(question), new_data_part({"root_dir": root_dir})],
            role=Role.ROLE_USER,
        )
        chunks = [
            get_stream_response_text(response)
            async for response in client.send_message(SendMessageRequest(message=message))
        ]
        return "\n".join(chunk for chunk in chunks if chunk)
    finally:
        await client.close()


def ask_code_reader(question: str, root_dir: str, base_url: str = DEFAULT_BASE_URL) -> str:
    """Sync wrapper so callers that aren't already in an event loop don't need asyncio."""
    return asyncio.run(ask_code_reader_async(question, root_dir, base_url))
