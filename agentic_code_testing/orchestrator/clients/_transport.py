import httpx
from a2a.client import ClientConfig, create_client
from a2a.types import Message, SendMessageRequest, TaskState
from a2a.helpers import get_message_text, get_stream_response_text, new_message, new_text_part


async def send_and_get_text(url: str, message: Message, timeout: float) -> str:
    """Sends a single message to an agent with no code-context interrupt and
    returns its text response.

    A non-interrupting agent server answers with exactly one non-streaming
    StreamResponse carrying a bare `message` (confirmed against a live
    server; never wrapped in a `task`), so the last non-empty text seen is
    the answer. Agents that can pause mid-task (planner_agent,
    codetest_writer_agent) must use `send_with_code_context` instead.
    """
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

    httpx_client = httpx.AsyncClient(timeout=timeout)
    client = await create_client(url, ClientConfig(streaming=True, httpx_client=httpx_client))
    try:
        while True:
            final = None
            async for response in client.send_message(SendMessageRequest(message=message)):
                final = response

            if final.HasField("status_update") and final.status_update.status.state == TaskState.TASK_STATE_INPUT_REQUIRED:
                question = get_message_text(final.status_update.status.message)
                answer = await ask_code_reader_async(question, root_dir)
                message = new_message(
                    parts=[new_text_part(answer)],
                    task_id=final.status_update.task_id,
                    context_id=final.status_update.context_id,
                )
                continue

            if final.HasField("task") and final.task.status.state == TaskState.TASK_STATE_INPUT_REQUIRED:
                question = get_message_text(final.task.status.message)
                answer = await ask_code_reader_async(question, root_dir)
                message = new_message(
                    parts=[new_text_part(answer)],
                    task_id=final.task.id,
                    context_id=final.task.context_id,
                )
                continue

            return get_stream_response_text(final)
    finally:
        await client.close()
