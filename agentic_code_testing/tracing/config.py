import os

from agentic_code_testing.llm.key_config import KeyConfig

_configured = False


def configure_tracing() -> None:
    """Bridges KeyConfig's LangSmith settings into os.environ.

    pydantic-settings loads the .key file into KeyConfig's own fields; it never
    touches os.environ. LangSmith's tracer, however, only reads
    LANGSMITH_TRACING/LANGSMITH_API_KEY/LANGSMITH_PROJECT/LANGSMITH_ENDPOINT
    from the environment, so this is the bridge that makes KeyConfig's values
    take effect. Idempotent, like setup_logging().
    """
    global _configured
    if _configured or not KeyConfig.langsmith_tracing:
        return

    os.environ["LANGSMITH_TRACING"] = "true"
    if KeyConfig.langsmith_api_key:
        os.environ["LANGSMITH_API_KEY"] = KeyConfig.langsmith_api_key
    os.environ["LANGSMITH_PROJECT"] = KeyConfig.langsmith_project
    if KeyConfig.langsmith_endpoint:
        os.environ["LANGSMITH_ENDPOINT"] = KeyConfig.langsmith_endpoint

    _configured = True
