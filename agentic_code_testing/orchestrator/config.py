from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).parent / ".env"
_ENV_FILE_ENCODING = "utf-8"


class _ServerConfig(BaseSettings):
    orchestrator_host: str = "127.0.0.1"
    orchestrator_port: int = 9999

    code_reader_agent_url: str = "http://127.0.0.1:9998"
    user_story_agent_url: str = "http://127.0.0.1:9995"
    planner_agent_url: str = "http://127.0.0.1:9996"
    codetest_writer_agent_url: str = "http://127.0.0.1:9997"

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding=_ENV_FILE_ENCODING,
        extra="ignore",
    )


ServerConfig = _ServerConfig()
