from langgraph.graph import StateGraph, START, END

from agentic_code_testing.agents.planner_agent.typed_schemas import PlannerAgentState, PlannerAgentContext
from agentic_code_testing.agents.planner_agent.plann_one_ac_agent.nodes.scenarios_generator import route_maybe_senarios, route_maybe_needs_context, generate_senarios
from agentic_code_testing.agents.planner_agent.plann_one_ac_agent.nodes.limit_senarios import limit_senarios
from agentic_code_testing.agents.planner_agent.plann_one_ac_agent.nodes.request_code_context import request_code_context

builder = StateGraph(PlannerAgentState, context_schema=PlannerAgentContext)

builder.add_node("generate_senarios", generate_senarios)
builder.add_node("limit_senarios", limit_senarios)
builder.add_node("request_code_context", request_code_context)

builder.add_edge(START, "generate_senarios")
builder.add_conditional_edges("generate_senarios",
                              route_maybe_needs_context,
                              {"needs_context": "request_code_context",
                               "limit_senarios": "limit_senarios"})
builder.add_edge("request_code_context", "generate_senarios")
builder.add_conditional_edges("limit_senarios",
                              route_maybe_senarios,
                              {"generate_again": "generate_senarios",
                               "category_done": END})


planner_agent_once_ac = builder.compile()
