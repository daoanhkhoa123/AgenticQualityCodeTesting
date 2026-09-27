import asyncio
import json
import logging

from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import TypeAdapter

from a2a.helpers import get_data_parts, new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater

from agentic_code_testing.agents.codetest_writer_agent.agent import invoke_codetest_writer_agent
from agentic_code_testing.agents.codetest_writer_agent.write_report.test_file_writer import GeneratedTestWriter
from agentic_code_testing.agents.planner_agent.typed_schemas import Scenario
from agentic_code_testing.llm.ollama_client import llm as default_llm

logger = logging.getLogger(__name__)

_SCENARIOS_ADAPTER = TypeAdapter(list[Scenario])


class CodetestWriterAgentExecutor(AgentExecutor):
    """Exposes invoke_codetest_writer_agent over the A2A protocol.

    scenarios/output_dir/root_dir/max_attempts come from the incoming
    message's data Part. Resolves no code-context interrupts itself --
    invoke_codetest_writer_agent falls back to a stock answer until the
    orchestrator wires a resolver in.
    """

    def __init__(self, llm: BaseChatModel | None = None):
        self._llm = llm or default_llm

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        data_parts = get_data_parts(context.message.parts) if context.message else []
        payload = next((d for d in data_parts if isinstance(d, dict) and d.get("scenarios")), None)
        if not payload:
            raise ValueError(
                "Message must include a data Part with a non-empty 'scenarios' "
                "field (matching list[Scenario]) plus 'output_dir' and 'root_dir'."
            )

        scenarios = _SCENARIOS_ADAPTER.validate_python(payload["scenarios"])
        output_dir = payload["output_dir"]
        root_dir = payload["root_dir"]
        # Data Parts round-trip JSON numbers as floats (protobuf Struct), so
        # coerce back to int at this boundary.
        max_attempts = int(payload.get("max_attempts", 3))

        results = await asyncio.to_thread(
            invoke_codetest_writer_agent,
            self._llm,
            scenarios,
            GeneratedTestWriter(),
            output_dir,
            root_dir,
            max_attempts,
        )

        await event_queue.enqueue_event(
            new_text_message(
                json.dumps([r.model_dump() for r in results]),
                context_id=context.context_id,
                task_id=context.task_id,
            )
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        if context.task_id and context.context_id:
            await TaskUpdater(event_queue, context.task_id, context.context_id).cancel()
