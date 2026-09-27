import asyncio
import json

from a2a.helpers import new_data_message, new_text_message
from a2a.server.agent_execution import RequestContext
from a2a.server.context import ServerCallContext
from a2a.types import SendMessageRequest, TaskState

from agentic_code_testing.agents.codetest_writer_agent import agent_executor as agent_executor_module
from agentic_code_testing.agents.codetest_writer_agent.agent_executor import CodetestWriterAgentExecutor
from agentic_code_testing.agents.codetest_writer_agent.typed_schemas import TestWriteResult
from agentic_code_testing.agents.planner_agent.typed_schemas import Scenario


class _FakeEventQueue:
    def __init__(self):
        self.events = []

    async def enqueue_event(self, event):
        self.events.append(event)


def _make_context(message, task_id, context_id):
    request = SendMessageRequest(message=message)
    return RequestContext(ServerCallContext(), request=request, task_id=task_id, context_id=context_id)


_SCENARIO = Scenario(
    scenario_id="S-1",
    story_id=1,
    category="happy path",
    priority="P0",
    test_type="unit",
    title="Add two numbers",
    description="Adds two numbers",
    expected_result="Sum is returned",
)

_RESULT = TestWriteResult(
    scenario_id="S-1",
    title="Add two numbers",
    status="passed",
    attempts=1,
)


def _fake_iter_codetest_writer_agent_steps(llm, scenarios, file_writer, output_dir, root_dir, max_attempts):
    answer = yield "Which file defines add()?"
    assert answer == "mathy.py defines add()."
    return [_RESULT]


def test_execute_asks_for_code_context_then_resumes_and_completes(monkeypatch):
    monkeypatch.setattr(
        agent_executor_module, "iter_codetest_writer_agent_steps", _fake_iter_codetest_writer_agent_steps
    )

    executor = CodetestWriterAgentExecutor(llm=object())
    queue = _FakeEventQueue()

    initial_message = new_data_message(
        {"scenarios": [_SCENARIO.model_dump()], "output_dir": "./out", "root_dir": "./project"}
    )
    context = _make_context(initial_message, task_id="task-1", context_id="ctx-1")

    asyncio.run(executor.execute(context, queue))

    assert "task-1" in executor._runs
    assert len(queue.events) == 2
    status_event = queue.events[1]
    assert status_event.status.state == TaskState.TASK_STATE_INPUT_REQUIRED
    assert status_event.status.message.parts[0].text == "Which file defines add()?"

    answer_message = new_text_message("mathy.py defines add().")
    resume_context = _make_context(answer_message, task_id="task-1", context_id="ctx-1")

    asyncio.run(executor.execute(resume_context, queue))

    assert "task-1" not in executor._runs
    assert len(queue.events) == 4
    completed_event = queue.events[3]
    assert completed_event.status.state == TaskState.TASK_STATE_COMPLETED
    results = json.loads(completed_event.status.message.parts[0].text)
    assert results[0]["scenario_id"] == "S-1"
    assert results[0]["status"] == "passed"


def test_cancel_clears_in_flight_run():
    executor = CodetestWriterAgentExecutor(llm=object())
    executor._runs["task-1"] = object()
    queue = _FakeEventQueue()
    context = _make_context(new_text_message("x"), task_id="task-1", context_id="ctx-1")

    asyncio.run(executor.cancel(context, queue))

    assert "task-1" not in executor._runs
