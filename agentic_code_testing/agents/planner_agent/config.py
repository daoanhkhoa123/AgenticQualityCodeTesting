from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).parent / ".env"
_ENV_FILE_ENCODING = "utf-8"


class _ServerConfig(BaseSettings):
    planner_agent_host: str = "127.0.0.1"
    planner_agent_port: int = 9996

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding=_ENV_FILE_ENCODING,
        extra="ignore",
    )


ServerConfig = _ServerConfig()
