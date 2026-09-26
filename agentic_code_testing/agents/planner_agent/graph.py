from langgraph.graph import StateGraph, START, END

from agentic_code_testing.agents.planner_agent.typed_schemas import PlannerAgentState, PlannerAgentContext
from agentic_code_testing.agents.planner_agent.extract_ac_agent.graph import extract_ac_graph

builder = StateGraph(PlannerAgentState, context_schema=PlannerAgentContext)

builder.add_node("extract_ac", extract_ac_graph)

builder.add_edge(START, "extract_ac")
builder.add_edge("extract_ac", END)

graph = builder.compile()
