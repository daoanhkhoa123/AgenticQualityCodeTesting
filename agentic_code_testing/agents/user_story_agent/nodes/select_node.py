from agentic_code_testing.agents.user_story_agent.typed_schemas import StoryAgentState, AUTOMATIC_FILL_STORY_STATE, PROCESS_STATE

def select_maybe_next_field(state: StoryAgentState) -> PROCESS_STATE:
    for field_name in AUTOMATIC_FILL_STORY_STATE:
        if not getattr(state, field_name):
            state.parsing_field_name = field_name
            return "parsing"

    state.parsing_field_name = None
    return "parsing_done"


def select_next_field_node(state: StoryAgentState) -> dict:
    """Node wrapper that persists select_maybe_next_field's choice.

    LangGraph rebuilds a fresh state instance per node/branch call, so the
    mutation inside select_maybe_next_field is otherwise lost; returning it
    here as a dict writes it back to the graph's channels.
    """
    select_maybe_next_field(state)
    return {"parsing_field_name": state.parsing_field_name}


def route_after_select(state: StoryAgentState) -> PROCESS_STATE:
    return "parsing" if state.parsing_field_name else "parsing_done"


