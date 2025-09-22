import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    log_level: str = os.getenv("LOG_LEVEL", "info")

    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "usersdb")
    db_user: str = os.getenv("DB_USER", "userapi")
    db_password: str = os.getenv("DB_PASSWORD", "userapi_password")

    email_api_base_url: str = os.getenv("EMAIL_API_BASE_URL", "http://localhost:8081")
    email_timeout_seconds: float = float(os.getenv("EMAIL_TIMEOUT_SECONDS", "3"))

    code_ttl_seconds: int = int(os.getenv("CODE_TTL_SECONDS", "60"))
    code_salt_bytes: int = int(os.getenv("CODE_SALT_BYTES", "16"))
    bcrypt_rounds: int = int(os.getenv("BCRYPT_ROUNDS", "12"))


def get_db_dsn() -> str:
    settings = Settings()
    return f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"


def get_settings() -> Settings:
    return Settings()
