from pydantic_settings import BaseSettings, SettingsConfigDict


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
    cors_origins: str = "http://localhost:3000,http://localhost:5173,https://linafp.pythonanywhere.com"

    @property
    def cors_origins_list(self) -> list[str]:
        cleaned = self.cors_origins.strip()
        if cleaned.startswith("[") and cleaned.endswith("]"):
            cleaned = cleaned[1:-1]
        cleaned = cleaned.replace('"', "").replace("'", "")
        return [origin.strip() for origin in cleaned.split(",") if origin.strip()]


settings = Settings()
