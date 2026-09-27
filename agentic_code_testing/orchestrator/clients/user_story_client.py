from a2a.helpers import new_data_message

from agentic_code_testing.agents.user_story_agent.typed_schemas import StoryAgentState
from agentic_code_testing.orchestrator.clients._transport import send_and_get_text
from agentic_code_testing.orchestrator.config import ServerConfig


async def ask_user_story_agent_async(file_path: str, story_id: int) -> StoryAgentState:
    message = new_data_message({"file_path": file_path, "story_id": story_id})
    text = await send_and_get_text(
        ServerConfig.user_story_agent_url, message, ServerConfig.user_story_agent_timeout_s
    )
    return StoryAgentState.model_validate_json(text)
