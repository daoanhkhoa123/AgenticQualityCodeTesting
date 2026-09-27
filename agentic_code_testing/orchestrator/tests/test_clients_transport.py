import asyncio

from a2a.helpers import new_data_message, new_text_message
from a2a.types import StreamResponse, Task, TaskStatus, TaskState

from agentic_code_testing.orchestrator.clients import _transport
from agentic_code_testing.orchestrator.clients import code_reader_client


class _FakeClient:
    def __init__(self, response_batches):
        self._response_batches = list(response_batches)
        self.sent_requests = []

    async def send_message(self, request):
        self.sent_requests.append(request)
        for response in self._response_batches.pop(0):
            yield response

    async def close(self):
        pass


def test_send_with_code_context_resumes_paused_task_and_returns_final_text(monkeypatch):
    question_message = new_text_message("Which file defines add()?")
    paused = StreamResponse(
        task=Task(
            id="task-1",
            context_id="ctx-1",
            status=TaskStatus(state=TaskState.TASK_STATE_INPUT_REQUIRED, message=question_message),
        )
    )
    completed = StreamResponse(message=new_text_message('[{"scenario_id": "S-1"}]'))

    fake_client = _FakeClient([[paused], [completed]])

    async def fake_create_client(url, client_config):
        return fake_client

    monkeypatch.setattr(_transport, "create_client", fake_create_client)

    async def fake_ask_code_reader_async(question, root_dir):
        assert question == "Which file defines add()?"
        assert root_dir == "./project"
        return "mathy.py defines add()."

    monkeypatch.setattr(code_reader_client, "ask_code_reader_async", fake_ask_code_reader_async)

    initial_message = new_data_message({"scenarios": []})
    text = asyncio.run(_transport.send_with_code_context("http://fake", initial_message, "./project", 5.0))

    assert text == '[{"scenario_id": "S-1"}]'
    assert len(fake_client.sent_requests) == 2

    follow_up = fake_client.sent_requests[1].message
    assert follow_up.task_id == "task-1"
    assert follow_up.context_id == "ctx-1"
    assert follow_up.parts[0].text == "mathy.py defines add()."


def test_send_with_code_context_returns_immediately_when_never_paused(monkeypatch):
    completed = StreamResponse(message=new_text_message("plain answer"))
    fake_client = _FakeClient([[completed]])

    async def fake_create_client(url, client_config):
        return fake_client

    monkeypatch.setattr(_transport, "create_client", fake_create_client)

    initial_message = new_data_message({"scenarios": []})
    text = asyncio.run(_transport.send_with_code_context("http://fake", initial_message, "./project", 5.0))

    assert text == "plain answer"
    assert len(fake_client.sent_requests) == 1
