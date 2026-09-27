import json

from a2a.helpers import new_data_message
from pydantic import TypeAdapter

from agentic_code_testing.agents.codetest_writer_agent.typed_schemas import TestWriteResult
from agentic_code_testing.agents.planner_agent.typed_schemas import Scenario
from agentic_code_testing.orchestrator.clients._transport import send_with_code_context
from agentic_code_testing.orchestrator.config import ServerConfig

_RESULTS_ADAPTER = TypeAdapter(list[TestWriteResult])


async def ask_codetest_writer_agent_async(
    scenarios: list[Scenario],
    output_dir: str,
    root_dir: str,
    max_attempts: int = 3,
) -> list[TestWriteResult]:
    payload = {
        "scenarios": [s.model_dump() for s in scenarios],
        "output_dir": output_dir,
        "root_dir": root_dir,
        "max_attempts": max_attempts,
    }

    message = new_data_message(payload)
    text = await send_with_code_context(
        ServerConfig.codetest_writer_agent_url, message, root_dir, ServerConfig.codetest_writer_agent_timeout_s
    )
    return _RESULTS_ADAPTER.validate_python(json.loads(text))
