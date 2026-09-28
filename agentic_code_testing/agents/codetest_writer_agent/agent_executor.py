import asyncio
import json
import logging

from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import TypeAdapter

from a2a.helpers import get_data_parts, new_task, new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import TaskState

from agentic_code_testing.agents.codetest_writer_agent.agent import iter_codetest_writer_agent_steps
from agentic_code_testing.agents.codetest_writer_agent.write_report.test_file_writer import GeneratedTestWriter
from agentic_code_testing.agents.planner_agent.typed_schemas import Scenario
from agentic_code_testing.llm.ollama_client import llm as default_llm

logger = logging.getLogger(__name__)

_SCENARIOS_ADAPTER = TypeAdapter(list[Scenario])


def _advance(gen, answer):
    """Runs in a worker thread. Returns ("question", str) or ("done", list[TestWriteResult])."""
    try:
        return ("question", gen.send(answer))
    except StopIteration as done:
        return ("done", done.value)


class CodetestWriterAgentExecutor(AgentExecutor):
    """Exposes invoke_codetest_writer_agent over the A2A protocol.

    scenarios/output_dir/root_dir/max_attempts/max_scenarios come from the incoming
    message's data Part. A code-context question is surfaced as an A2A
    input-required task state instead of resolved internally -- whoever
    calls this agent (the orchestrator) answers it (via code_reader_agent)
    and resumes the same task_id. Each in-flight generator is kept in
    `_runs`, keyed by task_id, for the life of that task -- execute() is
    invoked fresh by the SDK on every message, so this is the only place
    progress survives between calls.
    """

    def __init__(self, llm: BaseChatModel | None = None):
        self._llm = llm or default_llm
        self._runs: dict[str, object] = {}

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task_id = context.task_id

        if context.current_task is None:
            await event_queue.enqueue_event(
                new_task(task_id, context.context_id, TaskState.TASK_STATE_WORKING)
            )

        if task_id in self._runs:
            gen = self._runs[task_id]
            answer = context.get_user_input()
        else:
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
            max_scenarios = payload.get("max_scenarios")
            if max_scenarios is not None:
                max_scenarios = int(max_scenarios)

            gen = iter_codetest_writer_agent_steps(
                self._llm, scenarios, GeneratedTestWriter(), output_dir, root_dir, max_attempts, max_scenarios
            )
            self._runs[task_id] = gen
            answer = None

        kind, value = await asyncio.to_thread(_advance, gen, answer)
        updater = TaskUpdater(event_queue, task_id, context.context_id)

        if kind == "done":
            del self._runs[task_id]
            await updater.complete(
                message=new_text_message(
                    json.dumps([r.model_dump() for r in value]),
                    context_id=context.context_id,
                    task_id=task_id,
                )
            )
            return

        question = value
        await updater.requires_input(
            new_text_message(question, context_id=context.context_id, task_id=task_id)
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        if context.task_id and context.context_id:
            self._runs.pop(context.task_id, None)
            await TaskUpdater(event_queue, context.task_id, context.context_id).cancel()
