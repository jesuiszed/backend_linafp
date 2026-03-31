from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    env: str = "development"
    app_name: str = "LINAFP API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./linafp.db"
    secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = 10080
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            cleaned = value.strip()
            if cleaned.startswith("[") and cleaned.endswith("]"):
                cleaned = cleaned[1:-1]
            cleaned = cleaned.replace('"', "").replace("'", "")
            value = cleaned
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()
