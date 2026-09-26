from typing import Optional, Literal
from agentic_code_testing.agents.planner_agent.typed_schemas import PlannerAgentState, ScenarioCategory, PlannerAgentContext

SCENARIOS_STATE_MAP: dict[Optional[ScenarioCategory], Optional[ScenarioCategory]] = {
    None: "happy path",
    "happy path": "edge case",
    "edge case": "negative case",
    "negative case": None
}


def switch_category(state: PlannerAgentState) -> dict:
    return {"current_category":  SCENARIOS_STATE_MAP[state.current_category]}

SWITCH_MAYBE_CATEGORYT = Literal["go_end", "go_senarios"]
def route_maybe_category(state:PlannerAgentState) -> SWITCH_MAYBE_CATEGORYT:
    if state.current_category is None:
        return "go_end"
    return "go_senarios"
