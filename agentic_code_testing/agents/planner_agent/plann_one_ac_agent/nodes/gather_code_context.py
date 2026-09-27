import logging

from langgraph.runtime import Runtime

from agentic_code_testing.agents.code_reader_agent.client import ask_code_reader
from agentic_code_testing.agents.planner_agent.typed_schemas import PlannerAgentContext, PlannerAgentState

logger = logging.getLogger(__name__)


def gather_code_context(state: PlannerAgentState, runtime: Runtime[PlannerAgentContext]) -> dict:
    ac = runtime.context.acs[state.ac_idx]
    question = f"Find and summarize the code relevant to verifying this acceptance criterion:\n{ac}"

    try:
        code_context = ask_code_reader(question, runtime.context.root_dir, runtime.context.code_reader_base_url)
    except Exception:
        logger.warning("code_reader_agent unavailable; continuing without code context", exc_info=True)
        code_context = None

    return {"code_context": code_context}
