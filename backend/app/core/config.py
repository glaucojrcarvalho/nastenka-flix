from functools import lru_cache
from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Nastenka Flix"
    api_prefix: str = "/api"
    secret_key: str = "replace-me"
    access_token_expire_minutes: int = 1440
    algorithm: str = "HS256"
    database_url: str = "sqlite:///./backend/nastenka_flix.db"
    media_root: Path = Path(__file__).resolve().parents[3] / "media"
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    demo_username: str = "viewer"
    demo_display_name: str = "Viewer"
    demo_password: str = "changeme"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @computed_field
    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @computed_field
    @property
    def resolved_database_url(self) -> str:
        prefix = "sqlite:///./"
        if self.database_url.startswith(prefix):
            relative_path = self.database_url.removeprefix(prefix)
            absolute_path = (Path(__file__).resolve().parents[3] / relative_path).resolve()
            return f"sqlite:///{absolute_path}"
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
