import asyncio
import logging

from a2a.helpers import get_data_parts, new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater

from agentic_code_testing.orchestrator.agent import run_pipeline

logger = logging.getLogger(__name__)


class OrchestratorAgentExecutor(AgentExecutor):
    """Exposes run_pipeline over the A2A protocol.

    Stub for now: run_pipeline always raises NotImplementedError, so this
    reports that back as a normal (non-crashing) response rather than letting
    it surface as a server error, while the endpoint itself is already
    A2A-addressable.
    """

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        data_parts = get_data_parts(context.message.parts) if context.message else []
        payload = next((d for d in data_parts if isinstance(d, dict) and d.get("file_path")), None)
        if not payload:
            raise ValueError(
                "Message must include a data Part with a non-empty 'file_path' "
                "field plus 'story_id', 'output_dir', and 'root_dir'."
            )

        try:
            # Data Parts round-trip JSON numbers as floats (protobuf Struct),
            # so coerce back to int at this boundary.
            result = await asyncio.to_thread(
                run_pipeline,
                payload["file_path"],
                int(payload["story_id"]),
                payload["output_dir"],
                payload["root_dir"],
            )
        except NotImplementedError as exc:
            result = str(exc)

        await event_queue.enqueue_event(
            new_text_message(
                str(result),
                context_id=context.context_id,
                task_id=context.task_id,
            )
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        if context.task_id and context.context_id:
            await TaskUpdater(event_queue, context.task_id, context.context_id).cancel()
