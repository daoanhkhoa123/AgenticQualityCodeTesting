from agentic_code_testing.agents.user_story_agent.typed_schemas import StoryAgentState

LEADERBOARD_STORY_BODY = (
    "As a player, I want to be able to open a leaderboard that shows all players "
    "ranked by how much money they have, so that I can see how my progress compares "
    "to everyone else who has played the game.\n\n"
    'When I click the "Leaderboard" button from the main menu, a window should pop up '
    "showing a table of players sorted from highest money to lowest, with each row numbered "
    "by rank starting at 1. If I already have the leaderboard open and click the button again, "
    "it shouldn't open a second window on top of it. And if there's no save data yet, "
    "the leaderboard should still open normally, just without any rows, instead of crashing the game."
)

LEADERBOARD_SHORT_DESCRIPTION = (
    "As a player, I want to be able to open a leaderboard that shows all players "
    "ranked by how much money they have, so that I can see how my progress compares "
    "to everyone else who has played the game."
)

MOCK_STORY_AGENT_STATE = StoryAgentState(
    story_id=1,
    file_path=r"D:\AgenticQualityCodeTesting\user_inputs\user_stories\05_leaderboard_no_format.md",
    story_body=LEADERBOARD_STORY_BODY,
    name="money",
    description=LEADERBOARD_SHORT_DESCRIPTION,
    test_description=LEADERBOARD_STORY_BODY,
    acceptance_criteria="<Not found>",
    techinal_description="<Not found>",
    parsing_field_name=None,
)