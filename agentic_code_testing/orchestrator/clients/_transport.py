import httpx
from a2a.client import ClientConfig, create_client
from a2a.types import Message, Role, SendMessageRequest, TaskState
from a2a.helpers import get_message_text, get_stream_response_text, new_message, new_text_part

from agentic_code_testing.tracing.context import capture_trace_headers, inject_trace_metadata


def _extract_text(response) -> str:
    """Extracts text from a StreamResponse, preferring `status.message` for
    `task`/`status_update` payloads over `get_stream_response_text`'s
    artifacts-only handling of the `task` case (a2a-sdk gap)."""
    if response.HasField("task") and response.task.status.HasField("message"):
        return get_message_text(response.task.status.message)
    if response.HasField("status_update") and response.status_update.status.HasField("message"):
        return get_message_text(response.status_update.status.message)
    return get_stream_response_text(response)


async def send_and_get_text(url: str, message: Message, timeout: float) -> str:
    """Sends a single message to an agent with no code-context interrupt and
    returns its text response.

    A non-interrupting agent server answers with exactly one non-streaming
    StreamResponse carrying a bare `message` (confirmed against a live
    server; never wrapped in a `task`), so the last non-empty text seen is
    the answer. Agents that can pause mid-task (planner_agent,
    codetest_writer_agent) must use `send_with_code_context` instead.
    """
    inject_trace_metadata(message, capture_trace_headers())
    httpx_client = httpx.AsyncClient(timeout=timeout)
    client = await create_client(url, ClientConfig(streaming=False, httpx_client=httpx_client))
    try:
        request = SendMessageRequest(message=message)
        text = ""
        async for response in client.send_message(request):
            text = get_stream_response_text(response) or text
        return text
    finally:
        await client.close()


async def send_with_code_context(url: str, message: Message, root_dir: str, timeout: float) -> str:
    """Sends a message to an agent that may pause to ask for code context.

    If the agent's task enters TASK_STATE_INPUT_REQUIRED, the question is
    answered via code_reader_agent and the same task is resumed (same
    task_id/context_id) until it completes.
    """
    from agentic_code_testing.orchestrator.clients.code_reader_client import ask_code_reader_async

    trace_headers = capture_trace_headers()
    inject_trace_metadata(message, trace_headers)
    httpx_client = httpx.AsyncClient(timeout=timeout)
    client = await create_client(url, ClientConfig(streaming=True, httpx_client=httpx_client))
    try:
        while True:
            final = None
            text = ""
            async for response in client.send_message(SendMessageRequest(message=message)):
                final = response
                text = _extract_text(response) or text

            if final.HasField("status_update") and final.status_update.status.state == TaskState.TASK_STATE_INPUT_REQUIRED:
                question = get_message_text(final.status_update.status.message)
                answer = await ask_code_reader_async(question, root_dir)
                message = new_message(
                    parts=[new_text_part(answer)],
                    task_id=final.status_update.task_id,
                    context_id=final.status_update.context_id,
                    role=Role.ROLE_USER,
                )
                inject_trace_metadata(message, trace_headers)
                continue

            if final.HasField("task") and final.task.status.state == TaskState.TASK_STATE_INPUT_REQUIRED:
                question = get_message_text(final.task.status.message)
                answer = await ask_code_reader_async(question, root_dir)
                message = new_message(
                    parts=[new_text_part(answer)],
                    task_id=final.task.id,
                    context_id=final.task.context_id,
                    role=Role.ROLE_USER,
                )
                inject_trace_metadata(message, trace_headers)
                continue

            return text
    finally:
        await client.close()
