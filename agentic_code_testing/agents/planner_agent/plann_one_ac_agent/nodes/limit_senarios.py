from agentic_code_testing.agents.planner_agent.typed_schemas import PlannerAgentState

MAX_SCENARIOS_PER_CATEGORY = 3


def limit_senarios(state: PlannerAgentState) -> dict:
    count = sum(1 for scenario in state.scenarios if scenario.category == state.current_category)
    if count >= MAX_SCENARIOS_PER_CATEGORY:
        return {"is_category_covered": True}
    return {}
