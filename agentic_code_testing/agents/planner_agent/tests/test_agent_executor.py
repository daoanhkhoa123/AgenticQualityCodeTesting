import asyncio
import json

from a2a.helpers import get_data_parts, new_data_message, new_text_message
from a2a.server.agent_execution import RequestContext
from a2a.server.context import ServerCallContext
from a2a.types import SendMessageRequest, TaskState

from agentic_code_testing.agents.planner_agent import agent_executor as agent_executor_module
from agentic_code_testing.agents.planner_agent.agent_executor import PlannerAgentExecutor
from agentic_code_testing.agents.planner_agent.typed_schemas import Scenario
from agentic_code_testing.agents.user_story_agent.typed_schemas import StoryAgentState


class _FakeEventQueue:
    def __init__(self):
        self.events = []

    async def enqueue_event(self, event):
        self.events.append(event)


def _make_context(message, task_id, context_id):
    request = SendMessageRequest(message=message)
    return RequestContext(ServerCallContext(), request=request, task_id=task_id, context_id=context_id)


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

_SCENARIO = Scenario(
    scenario_id="S-1",
    story_id=1,
    category="happy path",
    priority="P0",
    test_type="unit",
    title="Successful login",
    description="User logs in",
    expected_result="User is logged in",
)


def _fake_iter_planning_agent_steps(llm, user_story, file_writer, output_dir, root_dir, max_acs):
    answer = yield ("question", "Which file defines the login handler?")
    assert answer == "auth.py defines it."
    return [_SCENARIO]


def _fake_iter_planning_agent_steps_with_progress(llm, user_story, file_writer, output_dir, root_dir, max_acs):
    answer = yield ("progress", _SCENARIO)
    assert answer is None
    return [_SCENARIO]


def test_execute_asks_for_code_context_then_resumes_and_completes(monkeypatch):
    monkeypatch.setattr(agent_executor_module, "iter_planning_agent_steps", _fake_iter_planning_agent_steps)

    executor = PlannerAgentExecutor(llm=object())
    queue = _FakeEventQueue()

    initial_message = new_data_message(
        {"user_story": _USER_STORY.model_dump(), "output_dir": "./out", "root_dir": "./project"}
    )
    context = _make_context(initial_message, task_id="task-1", context_id="ctx-1")

    asyncio.run(executor.execute(context, queue))

    assert "task-1" in executor._runs
    assert len(queue.events) == 1
    status_event = queue.events[0]
    assert status_event.status.state == TaskState.TASK_STATE_INPUT_REQUIRED
    assert status_event.status.message.parts[0].text == "Which file defines the login handler?"

    answer_message = new_text_message("auth.py defines it.")
    resume_context = _make_context(answer_message, task_id="task-1", context_id="ctx-1")

    asyncio.run(executor.execute(resume_context, queue))

    assert "task-1" not in executor._runs
    assert len(queue.events) == 2
    completed_event = queue.events[1]
    assert completed_event.status.state == TaskState.TASK_STATE_COMPLETED
    scenarios = json.loads(completed_event.status.message.parts[0].text)
    assert scenarios[0]["scenario_id"] == "S-1"


def test_execute_streams_progress_artifact_then_completes_in_one_call(monkeypatch):
    monkeypatch.setattr(
        agent_executor_module, "iter_planning_agent_steps", _fake_iter_planning_agent_steps_with_progress
    )

    executor = PlannerAgentExecutor(llm=object())
    queue = _FakeEventQueue()

    initial_message = new_data_message(
        {"user_story": _USER_STORY.model_dump(), "output_dir": "./out", "root_dir": "./project"}
    )
    context = _make_context(initial_message, task_id="task-1", context_id="ctx-1")

    asyncio.run(executor.execute(context, queue))

    # A single execute() call should stream the progress artifact and still
    # reach "done" without waiting for a second incoming message.
    assert "task-1" not in executor._runs
    assert len(queue.events) == 2

    artifact_event = queue.events[0]
    assert artifact_event.artifact.name == "scenario"
    scenario_data = get_data_parts(artifact_event.artifact.parts)[0]
    assert scenario_data["scenario_id"] == "S-1"

    completed_event = queue.events[1]
    assert completed_event.status.state == TaskState.TASK_STATE_COMPLETED
    scenarios = json.loads(completed_event.status.message.parts[0].text)
    assert scenarios[0]["scenario_id"] == "S-1"


def test_cancel_clears_in_flight_run():
    executor = PlannerAgentExecutor(llm=object())
    executor._runs["task-1"] = object()
    queue = _FakeEventQueue()
    context = _make_context(new_text_message("x"), task_id="task-1", context_id="ctx-1")

    asyncio.run(executor.cancel(context, queue))

    assert "task-1" not in executor._runs
