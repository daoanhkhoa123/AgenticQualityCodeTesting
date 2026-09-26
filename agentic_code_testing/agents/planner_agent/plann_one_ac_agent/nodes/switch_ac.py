from langgraph.runtime import Runtime
from typing import Literal
from agentic_code_testing.agents.planner_agent.typed_schemas import PlannerAgentState, PlannerAgentContext
from agentic_code_testing.agents.planner_agent.typed_schemas import PlannerAgentState, PlannerAgentContext


def switch_ac(state: PlannerAgentState) -> dict:
    return {"ac_idx": state.ac_idx + 1}

ROUTE_MAYBE_ACT = Literal["explore_ac", "go_end"]
def route_maybe_ac(state: PlannerAgentState, runtime:Runtime[PlannerAgentContext]) -> ROUTE_MAYBE_ACT:
    if state.ac_idx < len(runtime.context.acs):
        return "explore_ac"
    return "go_end"