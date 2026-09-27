import asyncio
import json
import logging

from langchain_core.language_models.chat_models import BaseChatModel

from a2a.helpers import get_data_parts, new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater

from agentic_code_testing.agents.code_reader_agent.client import ask_code_reader
from agentic_code_testing.agents.planner_agent.agent import invoke_planning_agent
from agentic_code_testing.agents.planner_agent.write_markdown.markdown_writer import MarkdownScenarioWriter
from agentic_code_testing.agents.user_story_agent.typed_schemas import StoryAgentState
from agentic_code_testing.llm.groq_client import llm as default_llm

logger = logging.getLogger(__name__)


class PlannerAgentExecutor(AgentExecutor):
    """Exposes invoke_planning_agent over the A2A protocol.

    user_story/output_dir/root_dir/max_acs come from the incoming message's
    data Part. code_context_resolver is wired to code_reader_agent's A2A
    client, matching the seam invoke_planning_agent already expects.
    """

    def __init__(self, llm: BaseChatModel | None = None):
        self._llm = llm or default_llm

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
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

        def code_context_resolver(question: str) -> str:
            return ask_code_reader(question, root_dir)

        scenarios = await asyncio.to_thread(
            invoke_planning_agent,
            self._llm,
            user_story,
            MarkdownScenarioWriter(),
            output_dir,
            root_dir,
            max_acs,
            code_context_resolver,
        )

        await event_queue.enqueue_event(
            new_text_message(
                json.dumps([s.model_dump() for s in scenarios]),
                context_id=context.context_id,
                task_id=context.task_id,
            )
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        if context.task_id and context.context_id:
            await TaskUpdater(event_queue, context.task_id, context.context_id).cancel()
