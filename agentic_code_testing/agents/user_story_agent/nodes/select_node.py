from agentic_code_testing.agents.user_story_agent.typed_schemas import StoryAgentState, AUTOMATIC_FILL_STORY_STATE, PROCESS_STATE


def select_next_field_node(state: StoryAgentState) -> dict:
    parsing_field_name = None
    for field_name in AUTOMATIC_FILL_STORY_STATE:
        if not getattr(state, field_name):
            parsing_field_name = field_name
            break

    return {"parsing_field_name": parsing_field_name}


def route_after_select(state: StoryAgentState) -> PROCESS_STATE:
    return "parsing" if state.parsing_field_name else "parsing_done"


