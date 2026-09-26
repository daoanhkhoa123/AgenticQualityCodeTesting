from agentic_code_testing.agents.planner_agent.typed_schemas import PlannerAgentState
from agentic_code_testing.agents.planner_agent.typed_schemas import PlannerAgentContext
from langgraph.runtime import Runtime


GENERATE_SENARIO_PROMPT = """

"""
def generate_senarios(state:PlannerAgentState, runtime: Runtime[PlannerAgentContext]):
