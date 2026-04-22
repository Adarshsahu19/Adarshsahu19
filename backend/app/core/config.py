from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'AI Voice Assistant API'
    app_env: str = 'development'
    app_host: str = '0.0.0.0'
    app_port: int = 8000
    openai_api_key: str | None = Field(default=None, alias='OPENAI_API_KEY')
    openai_model: str = 'gpt-4o-mini'


@lru_cache
def get_settings() -> Settings:
    return Settings()
