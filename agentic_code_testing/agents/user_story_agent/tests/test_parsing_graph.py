from pathlib import Path

import pytest

from agentic_code_testing.agents.user_story_agent.subgraphs.parsing_graph import parsing_graph
from agentic_code_testing.agents.user_story_agent.typed_schemas import StoryAgentContext, StoryAgentState
from agentic_code_testing.llm.groq_client import llm

SAMPLE_STORY_PATH = (
    Path(__file__).resolve().parents[4] / "user_inputs" / "user_stories" / "05_leaderboard_no_format.md"
)


@pytest.fixture
def initial_state() -> StoryAgentState:
    return StoryAgentState(
        story_id=1,
        file_path=str(SAMPLE_STORY_PATH),
        story_body="",
        name=None,
        description=None,
        test_description=None,
        acceptance_criteria=None,
        techinal_description=None,
        parsing_field_name=None,
    )


def test_parsing_graph_fills_all_fields(initial_state: StoryAgentState):
    result = parsing_graph.invoke(initial_state, context=StoryAgentContext(llm=llm))

    assert result["story_body"], "story_body should be populated by read_file_node"

    for field in ("name", "description", "test_description", "acceptance_criteria", "techinal_description"):
        assert result[field], f"{field} should be filled in (regex or LLM fallback)"

    for key, value in result.items():
        print(f"{key}:\n{value}\n")
