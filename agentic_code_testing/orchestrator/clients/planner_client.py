import json

from a2a.helpers import new_data_message
from pydantic import TypeAdapter

from agentic_code_testing.agents.planner_agent.typed_schemas import Scenario
from agentic_code_testing.agents.user_story_agent.typed_schemas import StoryAgentState
from agentic_code_testing.orchestrator.clients._transport import send_with_code_context
from agentic_code_testing.orchestrator.config import ServerConfig

_SCENARIOS_ADAPTER = TypeAdapter(list[Scenario])


async def ask_planner_agent_async(
    user_story: StoryAgentState,
    output_dir: str,
    root_dir: str,
    max_acs: int | None = None,
) -> list[Scenario]:
    payload = {"user_story": user_story.model_dump(), "output_dir": output_dir, "root_dir": root_dir}
    if max_acs is not None:
        payload["max_acs"] = max_acs

    message = new_data_message(payload)
    text = await send_with_code_context(
        ServerConfig.planner_agent_url, message, root_dir, ServerConfig.planner_agent_timeout_s
    )
    return _SCENARIOS_ADAPTER.validate_python(json.loads(text))
