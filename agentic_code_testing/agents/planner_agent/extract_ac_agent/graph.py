from agentic_code_testing.agents.planner_agent.extract_ac_agent.nodes import should_ask_human, asking_human, route_after_human
from agentic_code_testing.agents.planner_agent.extract_ac_agent.typed_schemas import ExtractACAgentState
from agentic_code_testing.agents.planner_agent.typed_schemas import PlannerAgentContext
from agentic_code_testing.agents.planner_agent.extract_ac_agent.extract_dimiliter_agent import extract_ac_node
from langgraph.graph import StateGraph, START, END

builder = StateGraph(ExtractACAgentState, context_schema=PlannerAgentContext)

builder.add_node("extract_ac_agent", extract_ac_node)
builder.add_node("asking_human", asking_human)

builder.add_edge(START, "extract_ac_agent")
builder.add_conditional_edges(
    "extract_ac_agent",
    should_ask_human,
    {"ask_human": "asking_human", "go_end": END}
)
builder.add_conditional_edges(
    "asking_human",
    route_after_human,
    {"accepted": END, "rejected": "extract_ac_agent"}
)

extract_ac_graph = builder.compile()