"""A2A client for calling this agent's server (see __main__.py / agent_executor.py)."""

import asyncio
import logging

import httpx
from a2a.client import ClientConfig, create_client
from a2a.helpers import get_stream_response_text, new_data_part, new_message
from a2a.types.a2a_pb2 import Role, SendMessageRequest
from pydantic import TypeAdapter

from agentic_code_testing.agents.planner_agent.config import ServerConfig
from agentic_code_testing.agents.planner_agent.typed_schemas import Scenario
from agentic_code_testing.agents.user_story_agent.typed_schemas import StoryAgentState

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = f"http://{ServerConfig.planner_agent_host}:{ServerConfig.planner_agent_port}"

# Planning drives one LLM call per acceptance criterion/category plus any
# code_reader_agent round trips, so this routinely runs far longer than a
# single request.
DEFAULT_TIMEOUT_SECONDS = 300.0

_SCENARIOS_ADAPTER = TypeAdapter(list[Scenario])


async def ask_planner_agent_async(
    user_story: StoryAgentState,
    output_dir: str,
    root_dir: str,
    max_acs: int | None = None,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> list[Scenario]:
    """Sends `user_story` to the planner_agent A2A server, scoped to `root_dir`."""
    client_config = ClientConfig(httpx_client=httpx.AsyncClient(timeout=timeout))
    client = await create_client(base_url, client_config=client_config)
    try:
        message = new_message(
            parts=[
                new_data_part(
                    {
                        "user_story": user_story.model_dump(),
                        "output_dir": str(output_dir),
                        "root_dir": root_dir,
                        "max_acs": max_acs,
                    }
                )
            ],
            role=Role.ROLE_USER,
        )
        chunks = [
            get_stream_response_text(response)
            async for response in client.send_message(SendMessageRequest(message=message))
        ]
        response_text = "".join(chunk for chunk in chunks if chunk)
        return _SCENARIOS_ADAPTER.validate_json(response_text)
    finally:
        await client.close()


def ask_planner_agent(
    user_story: StoryAgentState,
    output_dir: str,
    root_dir: str,
    max_acs: int | None = None,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> list[Scenario]:
    """Sync wrapper so callers that aren't already in an event loop don't need asyncio."""
    return asyncio.run(
        ask_planner_agent_async(user_story, output_dir, root_dir, max_acs, base_url, timeout)
    )
