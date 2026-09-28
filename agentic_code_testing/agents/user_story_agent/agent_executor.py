import logging

from langchain_core.language_models.chat_models import BaseChatModel

from a2a.helpers import get_data_parts, new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater

from agentic_code_testing.agents.user_story_agent.agent import invoke_user_story_agent
from agentic_code_testing.llm.ollama_client import llm as default_llm
from agentic_code_testing.tracing.context import extract_trace_headers, traced_run

logger = logging.getLogger(__name__)


class UserStoryAgentExecutor(AgentExecutor):
    """Exposes invoke_user_story_agent over the A2A protocol.

    file_path/story_id come from the incoming message's data Part, matching
    code_reader_agent's root_dir convention.
    """

    def __init__(self, llm: BaseChatModel | None = None):
        self._llm = llm or default_llm

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        data_parts = get_data_parts(context.message.parts) if context.message else []
        payload = next((d for d in data_parts if isinstance(d, dict) and d.get("file_path")), None)
        if not payload:
            raise ValueError(
                "Message must include a data Part with a non-empty 'file_path' field "
                "and a 'story_id' field."
            )

        file_path = payload["file_path"]
        # Data Parts round-trip JSON numbers as floats (protobuf Struct), so
        # coerce back to int at this boundary.
        story_id = int(payload["story_id"])

        with traced_run(extract_trace_headers(context.message)):
            result = invoke_user_story_agent(self._llm, file_path, story_id)

        await event_queue.enqueue_event(
            new_text_message(
                result.model_dump_json(),
                context_id=context.context_id,
                task_id=context.task_id,
            )
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        if context.task_id and context.context_id:
            await TaskUpdater(event_queue, context.task_id, context.context_id).cancel()
