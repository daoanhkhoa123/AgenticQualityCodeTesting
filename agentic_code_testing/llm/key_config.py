from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).parent / ".key"
_ENV_FILE_ENCODING = "utf-8"


class _KeyConfig(BaseSettings):
    groq_api_key: str
    ollama_base_url: str
    ollama_model: str
    ollama_timeout_seconds: float = 60.0

    langsmith_tracing: bool = False
    langsmith_api_key: str | None = None
    langsmith_project: str = "agentic-code-testing"
    langsmith_endpoint: str | None = None

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding=_ENV_FILE_ENCODING,
        extra="ignore",
    )


KeyConfig = _KeyConfig()  # type: ignore
