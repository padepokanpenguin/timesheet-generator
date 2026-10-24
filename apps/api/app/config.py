from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Jira Cloud. Untuk pengembangan lokal pakai email + API token.
    # TODO: ganti dengan OAuth 2.0 (3LO) per pengguna (Authlib) untuk produksi.
    jira_base_url: str = ""  # contoh: https://perusahaan.atlassian.net
    jira_email: str = ""
    jira_api_token: str = ""
    jira_story_points_field: str = "customfield_10016"  # ID field Story Points berbeda per site

    # True = pakai data contoh (tanpa Jira) supaya UI dan Excel bisa dicoba langsung.
    jira_mock: bool = True

    cors_origins: list[str] = ["http://localhost:5173"]
    storage_dir: Path = Path("storage")  # TODO: ganti ke S3-compatible + enkripsi
    database_url: str = "postgresql+psycopg://timesheet:timesheet@localhost:5432/timesheet"
    redis_url: str = "redis://localhost:6379/0"
    postgres_port: int = 5432
    redis_port: int = 6379


@lru_cache
def get_settings() -> Settings:
    return Settings()
