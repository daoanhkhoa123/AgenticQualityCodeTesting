from collections.abc import Iterator
from contextlib import contextmanager

from langsmith.run_helpers import get_current_run_tree, tracing_context

from a2a.types import Message


def capture_trace_headers() -> dict[str, str]:
    """Captures the active LangSmith run's context as a small dict of headers.

    Returns {} when tracing is disabled or there is no active run, so callers
    downstream (inject_trace_metadata, traced_run) become no-ops.
    """
    run_tree = get_current_run_tree()
    if run_tree is None:
        return {}
    return run_tree.to_headers()


def inject_trace_metadata(message: Message, headers: dict[str, str]) -> None:
    """Stashes trace headers on an outgoing A2A message's unused metadata field."""
    if headers:
        message.metadata.update(headers)


def extract_trace_headers(message: Message | None) -> dict[str, str]:
    """Reads back whatever trace headers inject_trace_metadata stashed, or {}.

    message is None for an A2A request_context with no incoming message (a
    plain resume/poll) -- executors pass context.message through unchecked.
    """
    if message is None:
        return {}
    return dict(message.metadata)


@contextmanager
def traced_run(headers: dict[str, str]) -> Iterator[None]:
    """Re-attaches to the caller's LangSmith trace for the wrapped block.

    With an empty `headers` (tracing disabled, or the caller sent none), this
    is a no-op and code inside runs untraced/as its own root, same as today.
    """
    with tracing_context(parent=headers or None):
        yield
