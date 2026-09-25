from langgraph.graph import StateGraph, START, END

from agentic_code_testing.agents.user_story_agent.typed_schemas import StoryAgentState, StoryAgentContext
from agentic_code_testing.agents.user_story_agent.nodes.parsing_nodes import (
    read_file_node,
    parse_regex_prefill_node,
    parsing_single_field_node,
)
from agentic_code_testing.agents.user_story_agent.nodes.select_node import (
    select_next_field_node,
    route_after_select,
)

builder = StateGraph(StoryAgentState, context_schema=StoryAgentContext)

builder.add_node("read_file", read_file_node)
builder.add_node("parse_regex", parse_regex_prefill_node)
builder.add_node("select_next_field", select_next_field_node)
builder.add_node("parse_field", parsing_single_field_node)

builder.add_edge(START, "read_file")
builder.add_edge("read_file", "parse_regex")
builder.add_edge("parse_regex", "select_next_field")
builder.add_conditional_edges(
    "select_next_field",
    route_after_select,
    {"parsing": "parse_field", "parsing_done": END},
)
builder.add_edge("parse_field", "select_next_field")

parsing_graph = builder.compile()
