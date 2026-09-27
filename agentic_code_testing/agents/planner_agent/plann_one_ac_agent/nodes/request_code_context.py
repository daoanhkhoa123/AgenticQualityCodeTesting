from langgraph.types import interrupt

from agentic_code_testing.agents.planner_agent.typed_schemas import PlannerAgentState


def request_code_context(state: PlannerAgentState) -> dict:
    answer = interrupt({"question": state.pending_code_context_question})
    if not isinstance(answer, str):
        answer = str(answer)

    combined = f"{state.code_context}\n\n{answer}" if state.code_context else answer
    return {"code_context": combined, "pending_code_context_question": None}
