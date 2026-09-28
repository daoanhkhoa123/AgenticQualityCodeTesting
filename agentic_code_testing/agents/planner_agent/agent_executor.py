import asyncio
import json
import logging

from langchain_core.language_models.chat_models import BaseChatModel

from a2a.helpers import get_data_parts, new_data_part, new_task, new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import TaskState

from agentic_code_testing.agents.planner_agent.agent import iter_planning_agent_steps
from agentic_code_testing.agents.planner_agent.write_markdown.markdown_writer import MarkdownScenarioWriter
from agentic_code_testing.agents.user_story_agent.typed_schemas import StoryAgentState
from agentic_code_testing.llm.ollama_client import llm as default_llm
from agentic_code_testing.tracing.context import extract_trace_headers, traced_run

logger = logging.getLogger(__name__)


def _advance(gen, answer):
    """Runs in a worker thread. Returns ("question", str), ("progress", Scenario),
    or ("done", list[Scenario])."""
    try:
        return gen.send(answer)
    except StopIteration as done:
        return ("done", done.value)


class PlannerAgentExecutor(AgentExecutor):
    """Exposes invoke_planning_agent over the A2A protocol.

    user_story/output_dir/root_dir/max_acs come from the incoming message's
    data Part. A code-context question is surfaced as an A2A input-required
    task state instead of resolved internally -- whoever calls this agent
    (the orchestrator) answers it (via code_reader_agent) and resumes the
    same task_id. Each in-flight generator is kept in `_runs`, keyed by
    task_id, for the life of that task -- execute() is invoked fresh by the
    SDK on every message, so this is the only place progress survives
    between calls.
    """

    def __init__(self, llm: BaseChatModel | None = None):
        self._llm = llm or default_llm
        self._runs: dict[str, tuple[object, dict[str, str]]] = {}

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task_id = context.task_id

        if context.current_task is None:
            await event_queue.enqueue_event(
                new_task(task_id, context.context_id, TaskState.TASK_STATE_WORKING)
            )

        if task_id in self._runs:
            gen, trace_headers = self._runs[task_id]
            answer = context.get_user_input()
        else:
            data_parts = get_data_parts(context.message.parts) if context.message else []
            payload = next((d for d in data_parts if isinstance(d, dict) and d.get("user_story")), None)
            if not payload:
                raise ValueError(
                    "Message must include a data Part with a non-empty 'user_story' "
                    "field (matching StoryAgentState) plus 'output_dir' and 'root_dir'."
                )

            user_story = StoryAgentState.model_validate(payload["user_story"])
            output_dir = payload["output_dir"]
            root_dir = payload["root_dir"]
            # Data Parts round-trip JSON numbers as floats (protobuf Struct), so
            # coerce back to int at this boundary before it hits acs[:max_acs].
            raw_max_acs = payload.get("max_acs")
            max_acs = int(raw_max_acs) if raw_max_acs is not None else None

            gen = iter_planning_agent_steps(
                self._llm, user_story, MarkdownScenarioWriter(), output_dir, root_dir, max_acs
            )
            trace_headers = extract_trace_headers(context.message)
            self._runs[task_id] = (gen, trace_headers)
            answer = None

        updater = TaskUpdater(event_queue, task_id, context.context_id)
        while True:
            with traced_run(trace_headers):
                kind, value = await asyncio.to_thread(_advance, gen, answer)

            if kind == "done":
                del self._runs[task_id]
                await updater.complete(
                    message=new_text_message(
                        json.dumps([s.model_dump() for s in value]),
                        context_id=context.context_id,
                        task_id=task_id,
                    )
                )
                return

            if kind == "progress":
                await updater.add_artifact(
                    parts=[new_data_part(value.model_dump())],
                    name="scenario",
                )
                answer = None
                continue

            question = value
            await updater.requires_input(
                new_text_message(question, context_id=context.context_id, task_id=task_id)
            )
            return

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        if context.task_id and context.context_id:
            self._runs.pop(context.task_id, None)
            await TaskUpdater(event_queue, context.task_id, context.context_id).cancel()
