from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from agentic_code_testing.agents.planner_agent.extract_ac_agent.graph import builder, extract_ac_graph
from agentic_code_testing.agents.planner_agent.extract_ac_agent.typed_schemas import ExtractACAgentState
from agentic_code_testing.agents.planner_agent.tests.mock_data import MOCK_STORY_AGENT_STATE
from agentic_code_testing.agents.planner_agent.typed_schemas import PlannerAgentContext
from agentic_code_testing.agents.user_story_agent.nodes.parsing_nodes import NOT_FOUND_TOKEN
from agentic_code_testing.llm.groq_client import llm

BULLETED_AC = (
    "- User can open the leaderboard from the main menu\n"
    "- Rows are sorted by money, highest first\n"
    "- Reopening the leaderboard does not stack a second window\n"
    "- An empty save still opens the leaderboard with no rows\n"
)

def test_extract_ac_graph_ends_when_criteria_found():
    user_story = MOCK_STORY_AGENT_STATE.model_copy(update={"acceptance_criteria": BULLETED_AC})
    state = ExtractACAgentState(user_story=user_story)
    result = extract_ac_graph.invoke(state, context=PlannerAgentContext(llm=llm))

    assert "__interrupt__" not in result, "criteria was found, so no human review should be needed"
    assert result["acs"], "acs should be populated by extract_ac_agent"
    assert result["user_story"].story_body == "", "story_body should be cleared to save context"

    for ac in result["acs"]:
        print(f"- {ac}")


def test_extract_ac_graph_human_review_loop():
    graph = builder.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "extract-ac-human-review-test"}}
    context = PlannerAgentContext(llm=llm)

    user_story = MOCK_STORY_AGENT_STATE.model_copy(update={"acceptance_criteria": NOT_FOUND_TOKEN})
    state = ExtractACAgentState(user_story=user_story)
    result = graph.invoke(state, config=config, context=context)

    assert "__interrupt__" in result, "criteria was not found, so the graph should pause for human review"
    payload = result["__interrupt__"][0].value
    assert "acs" in payload and "question" in payload

    result = graph.invoke(
        Command(resume={"accepted": False, "feedback": "number the criteria instead of bulleting them"}),
        config=config,
        context=context,
    )
    assert "__interrupt__" in result, "rejection should route back to extract_ac_agent and ask again"

    final = graph.invoke(Command(resume={"accepted": True}), config=config, context=context)

    assert "__interrupt__" not in final, "acceptance should end the graph"
    print(f"acs:\n{final['acs']}\n")
