import logging
from typing import TypeVar

from langchain_core.runnables import Runnable

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Occasionally the model returns something the structured-output parser can't
# turn into the expected pydantic type at all (e.g. it echoes the JSON schema
# instead of an instance, or the Groq API rejects the completion outright) --
# a transient formatting hiccup, not a problem with the drafted test or source
# code. A couple of raw retries absorbs that without crashing the whole batch.
MAX_RAW_RETRIES = 2


def invoke_structured(chain: Runnable, inputs: dict, expected_type: type[T]) -> T:
    last_error: Exception | None = None

    for attempt in range(MAX_RAW_RETRIES + 1):
        try:
            result = chain.invoke(inputs)
        except Exception as exc:
            last_error = exc
            logger.warning(
                "Structured output call raised on attempt %d/%d: %s",
                attempt + 1, MAX_RAW_RETRIES + 1, exc,
            )
            continue

        if isinstance(result, expected_type):
            return result

        last_error = TypeError(f"Expected {expected_type.__name__} from structured output, got {type(result)}")
        logger.warning(str(last_error))

    raise last_error
