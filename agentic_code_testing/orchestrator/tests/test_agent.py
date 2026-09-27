import asyncio

from agentic_code_testing.agents.codetest_writer_agent.typed_schemas import TestWriteResult
from agentic_code_testing.agents.planner_agent.typed_schemas import Scenario
from agentic_code_testing.agents.user_story_agent.typed_schemas import StoryAgentState
from agentic_code_testing.orchestrator import agent as orchestrator_agent

_USER_STORY = StoryAgentState(
    story_id=1,
    file_path="./stories/US-1.md",
    story_body="As a user...",
    name="Login",
    description="User can log in",
    test_description=None,
    acceptance_criteria="Given/When/Then",
    techinal_description=None,
    parsing_field_name=None,
)

_SCENARIOS = [
    Scenario(
        scenario_id="S-1",
        story_id=1,
        category="happy path",
        priority="P0",
        test_type="unit",
        title="Successful login",
        description="User logs in with valid credentials",
        expected_result="User is logged in",
    )
]

_TEST_RESULTS = [
    TestWriteResult(
        scenario_id="S-1",
        title="Successful login",
        status="passed",
        attempts=1,
    )
]


def test_run_pipeline_calls_stages_in_order_and_assembles_result(monkeypatch, tmp_path):
    calls = []

    async def fake_ask_user_story_agent_async(file_path, story_id):
        calls.append("user_story")
        assert file_path == "./stories/US-1.md"
        assert story_id == 1
        return _USER_STORY

    async def fake_ask_planner_agent_async(user_story, output_dir, root_dir):
        calls.append("planner")
        assert user_story == _USER_STORY
        assert output_dir == "./out"
        assert root_dir == "./project"
        return _SCENARIOS

    async def fake_ask_codetest_writer_agent_async(scenarios, output_dir, root_dir):
        calls.append("codetest_writer")
        assert scenarios == _SCENARIOS
        return _TEST_RESULTS

    monkeypatch.setattr(orchestrator_agent, "ask_user_story_agent_async", fake_ask_user_story_agent_async)
    monkeypatch.setattr(orchestrator_agent, "ask_planner_agent_async", fake_ask_planner_agent_async)
    monkeypatch.setattr(orchestrator_agent, "ask_codetest_writer_agent_async", fake_ask_codetest_writer_agent_async)

    result = asyncio.run(
        orchestrator_agent.run_pipeline("./stories/US-1.md", 1, "./out", "./project", pipeline_output_dir=tmp_path)
    )

    assert calls == ["user_story", "planner", "codetest_writer"]
    assert result.story_id == 1
    assert result.user_story == _USER_STORY
    assert result.scenarios == _SCENARIOS
    assert result.test_results == _TEST_RESULTS

    written_path = tmp_path / "story-1.md"
    assert written_path.exists()
    content = written_path.read_text(encoding="utf-8")
    assert _SCENARIOS[0].title in content
    assert _TEST_RESULTS[0].status in content


def test_run_pipeline_carries_empty_scenarios_through(monkeypatch, tmp_path):
    async def fake_ask_user_story_agent_async(file_path, story_id):
        return _USER_STORY

    async def fake_ask_planner_agent_async(user_story, output_dir, root_dir):
        return []

    async def fake_ask_codetest_writer_agent_async(scenarios, output_dir, root_dir):
        assert scenarios == []
        return []

    monkeypatch.setattr(orchestrator_agent, "ask_user_story_agent_async", fake_ask_user_story_agent_async)
    monkeypatch.setattr(orchestrator_agent, "ask_planner_agent_async", fake_ask_planner_agent_async)
    monkeypatch.setattr(orchestrator_agent, "ask_codetest_writer_agent_async", fake_ask_codetest_writer_agent_async)

    result = asyncio.run(
        orchestrator_agent.run_pipeline("./stories/US-1.md", 1, "./out", "./project", pipeline_output_dir=tmp_path)
    )

    assert result.scenarios == []
    assert result.test_results == []
    assert (tmp_path / "story-1.md").exists()
