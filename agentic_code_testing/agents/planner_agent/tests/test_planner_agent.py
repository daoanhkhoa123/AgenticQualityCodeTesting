from agentic_code_testing.agents.planner_agent.agent import invoke_planning_agent
from agentic_code_testing.agents.planner_agent.tests.mock_data import MOCK_STORY_AGENT_STATE
from agentic_code_testing.agents.planner_agent.typed_schemas import Scenario
from agentic_code_testing.agents.planner_agent.write_markdown.markdown_writer import MarkdownScenarioWriter
from agentic_code_testing.agents.user_story_agent.nodes.parsing_nodes import NOT_FOUND_TOKEN
from agentic_code_testing.llm.groq_client import llm

# def test_invoke_planning_agent_writes_scenarios_to_markdown(tmp_path):
#     user_story = MOCK_STORY_AGENT_STATE.model_copy(update={"acceptance_criteria": BULLETED_AC})
#     file_writer = MarkdownScenarioWriter()

#     scenarios = invoke_planning_agent(llm, user_story, file_writer, tmp_path)

#     assert scenarios, "planner agent should generate at least one scenario"
#     assert all(isinstance(scenario, Scenario) for scenario in scenarios)

#     written_files = sorted(tmp_path.glob("*.md"))
#     assert len(written_files) == len(scenarios), "one markdown file should be written per scenario"

#     for scenario in scenarios:
#         expected_path = tmp_path / f"{scenario.scenario_id}.md"
#         assert expected_path.exists()
#         content = expected_path.read_text(encoding="utf-8")
#         assert scenario.title in content

#     print(f"scenarios:\n{scenarios}\n")


def test_invoke_planning_agent_without_bulleted_ac(tmp_path):
    user_story = MOCK_STORY_AGENT_STATE.model_copy(update={"acceptance_criteria": NOT_FOUND_TOKEN})
    file_writer = MarkdownScenarioWriter()

    scenarios = invoke_planning_agent(llm, user_story, file_writer, tmp_path, max_acs=2)

    assert all(isinstance(scenario, Scenario) for scenario in scenarios)

    written_files = sorted(tmp_path.glob("*.md"))
    assert len(written_files) == len(scenarios), "one markdown file should be written per scenario"

    for scenario in scenarios:
        expected_path = tmp_path / f"{scenario.scenario_id}.md"
        assert expected_path.exists()
        content = expected_path.read_text(encoding="utf-8")
        assert scenario.title in content

    print(f"scenarios:\n{scenarios}\n")
