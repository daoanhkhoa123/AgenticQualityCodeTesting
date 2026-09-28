from a2a.helpers import new_data_part, new_message, new_text_part
from a2a.types import Role

from agentic_code_testing.orchestrator.clients._transport import send_and_get_text
from agentic_code_testing.orchestrator.config import ServerConfig


async def ask_code_reader_async(question: str, root_dir: str) -> str:
    """Answers a code-context question a paused planner_agent/codetest_writer_agent
    task is asking, called from `_transport.send_with_code_context`'s resume loop."""
    message = new_message(
        parts=[new_text_part(question), new_data_part({"root_dir": root_dir})],
        role=Role.ROLE_USER,
    )
    return await send_and_get_text(
        ServerConfig.code_reader_agent_url, message, ServerConfig.code_reader_agent_timeout_s
    )
