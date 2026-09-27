import logging

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage

from a2a.helpers import get_data_parts, new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater

from agentic_code_testing.agents.code_reader_agent.agent import create_code_reader_agent
from agentic_code_testing.llm.groq_client import llm as default_llm

logger = logging.getLogger(__name__)


class CodeReaderAgentExecutor(AgentExecutor):
    """Exposes create_code_reader_agent over the A2A protocol.

    root_dir comes from the incoming message's data Part (per-request), matching
    the trust-boundary note in agent.py: the caller sets root_dir, never the LLM.
    """

    def __init__(self, llm: BaseChatModel | None = None):
        self._llm = llm or default_llm

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        question = context.get_user_input()
        data_parts = get_data_parts(context.message.parts) if context.message else []
        root_dir = next(
            (d["root_dir"] for d in data_parts if isinstance(d, dict) and d.get("root_dir")),
            None,
        )
        if not root_dir:
            raise ValueError(
                "Message must include a data Part with a non-empty 'root_dir' field."
            )

        agent = create_code_reader_agent(self._llm, root_dir)
        result = await agent.ainvoke({"messages": [HumanMessage(content=question)]})
        answer = result["messages"][-1].content

        await event_queue.enqueue_event(
            new_text_message(
                answer,
                context_id=context.context_id,
                task_id=context.task_id,
            )
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        if context.task_id and context.context_id:
            await TaskUpdater(event_queue, context.task_id, context.context_id).cancel()
