"""A2A client for calling this agent's server (see __main__.py / agent_executor.py)."""

import asyncio
import logging

import httpx
from a2a.client import ClientConfig, create_client
from a2a.helpers import get_stream_response_text, new_data_part, new_message
from a2a.types.a2a_pb2 import Role, SendMessageRequest

from agentic_code_testing.agents.user_story_agent.config import ServerConfig
from agentic_code_testing.agents.user_story_agent.typed_schemas import StoryAgentState

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = f"http://{ServerConfig.user_story_agent_host}:{ServerConfig.user_story_agent_port}"
DEFAULT_TIMEOUT_SECONDS = 60.0


async def ask_user_story_agent_async(
    file_path: str,
    story_id: int,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> StoryAgentState:
    """Sends `file_path`/`story_id` to the user_story_agent A2A server."""
    client_config = ClientConfig(httpx_client=httpx.AsyncClient(timeout=timeout))
    client = await create_client(base_url, client_config=client_config)
    try:
        message = new_message(
            parts=[new_data_part({"file_path": file_path, "story_id": story_id})],
            role=Role.ROLE_USER,
        )
        chunks = [
            get_stream_response_text(response)
            async for response in client.send_message(SendMessageRequest(message=message))
        ]
        response_text = "".join(chunk for chunk in chunks if chunk)
        return StoryAgentState.model_validate_json(response_text)
    finally:
        await client.close()


def ask_user_story_agent(
    file_path: str,
    story_id: int,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> StoryAgentState:
    """Sync wrapper so callers that aren't already in an event loop don't need asyncio."""
    return asyncio.run(ask_user_story_agent_async(file_path, story_id, base_url, timeout))
