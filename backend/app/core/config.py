from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    api_port: int = 8000
    database_url: str = "sqlite:///./smart_tourist_mobility.db"
    timezone: str = "Asia/Kolkata"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
