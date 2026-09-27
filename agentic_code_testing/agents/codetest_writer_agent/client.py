"""A2A client for calling this agent's server (see __main__.py / agent_executor.py)."""

import asyncio
import logging

import httpx
from a2a.client import ClientConfig, create_client
from a2a.helpers import get_stream_response_text, new_data_part, new_message
from a2a.types.a2a_pb2 import Role, SendMessageRequest
from pydantic import TypeAdapter

from agentic_code_testing.agents.codetest_writer_agent.config import ServerConfig
from agentic_code_testing.agents.codetest_writer_agent.typed_schemas import TestWriteResult
from agentic_code_testing.agents.planner_agent.typed_schemas import Scenario

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = (
    f"http://{ServerConfig.codetest_writer_agent_host}:{ServerConfig.codetest_writer_agent_port}"
)

# Each scenario can go through several draft/run/classify attempts plus
# code_reader_agent round trips and a real pytest subprocess run, so this
# routinely runs far longer than a single request.
DEFAULT_TIMEOUT_SECONDS = 600.0

_RESULTS_ADAPTER = TypeAdapter(list[TestWriteResult])


async def ask_codetest_writer_agent_async(
    scenarios: list[Scenario],
    output_dir: str,
    root_dir: str,
    max_attempts: int = 3,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> list[TestWriteResult]:
    """Sends `scenarios` to the codetest_writer_agent A2A server, scoped to `root_dir`."""
    client_config = ClientConfig(httpx_client=httpx.AsyncClient(timeout=timeout))
    client = await create_client(base_url, client_config=client_config)
    try:
        message = new_message(
            parts=[
                new_data_part(
                    {
                        "scenarios": [s.model_dump() for s in scenarios],
                        "output_dir": str(output_dir),
                        "root_dir": root_dir,
                        "max_attempts": max_attempts,
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
        return _RESULTS_ADAPTER.validate_json(response_text)
    finally:
        await client.close()


def ask_codetest_writer_agent(
    scenarios: list[Scenario],
    output_dir: str,
    root_dir: str,
    max_attempts: int = 3,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> list[TestWriteResult]:
    """Sync wrapper so callers that aren't already in an event loop don't need asyncio."""
    return asyncio.run(
        ask_codetest_writer_agent_async(
            scenarios, output_dir, root_dir, max_attempts, base_url, timeout
        )
    )
