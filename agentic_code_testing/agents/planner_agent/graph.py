from langgraph.graph import StateGraph, START, END

from agentic_code_testing.agents.planner_agent.typed_schemas import PlannerAgentState, PlannerAgentContext
from agentic_code_testing.agents.planner_agent.extract_ac_agent.graph import extract_ac_graph
from agentic_code_testing.agents.planner_agent.nodes.scenarios_generator import route_maybe_senarios, generate_senarios
from agentic_code_testing.agents.planner_agent.nodes.switch_category import switch_category, route_maybe_category

builder = StateGraph(PlannerAgentState, context_schema=PlannerAgentContext)

builder.add_node("route_maybe_category", route_maybe_category)
builder.add_node("switch_category", switch_category)
builder.add_node("route_maybe_senarios", route_maybe_senarios)
builder.add_node("generate_senarios", generate_senarios)

builder.add_edge(START, "switch_category")
builder.add_conditional_edges("switch_category",
                              route_maybe_category,
                              {"go_end": END,
                               "go_senarios": "generate_senarios"})
builder.add_conditional_edges("generate_senarios",
                              route_maybe_senarios,
                              {"generate_again": "generate_senarios",
                               "next_category": "switch_category"})


planner_agent = builder.compile()
