from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).parent / ".env"
_ENV_FILE_ENCODING = "utf-8"


class _ServerConfig(BaseSettings):
    user_story_agent_host: str = "127.0.0.1"
    user_story_agent_port: int = 9995

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding=_ENV_FILE_ENCODING,
        extra="ignore",
    )


ServerConfig = _ServerConfig()
