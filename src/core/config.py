"""
Application configuration using pydantic-settings.
Loads settings from environment variables and .env file.
"""

from typing import Literal

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Todo Backend API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    # Database
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/todo_db",
        description="PostgreSQL database URL with asyncpg driver",
    )
    DB_POOL_SIZE: int = Field(default=5, ge=1, le=50)
    DB_MAX_OVERFLOW: int = Field(default=10, ge=0, le=50)
    DB_POOL_TIMEOUT: int = Field(default=30, ge=1, le=300)
    DB_POOL_RECYCLE: int = Field(default=3600, ge=300)
    DB_ECHO: bool = False

    # JWT Settings
    SECRET_KEY: str = Field(
        default="CHANGE_ME_IN_PRODUCTION_USE_STRONG_SECRET_KEY",
        min_length=32,
        description="Secret key for JWT token signing (min 32 chars)",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, ge=1, le=1440)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, ge=1, le=30)

    # CORS Settings
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Comma-separated allowed CORS origins",
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "*"
    CORS_ALLOW_HEADERS: str = "*"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # Security
    PASSWORD_MIN_LENGTH: int = Field(default=8, ge=8, le=128)
    PASSWORD_MAX_LENGTH: int = Field(default=128, ge=8, le=256)

    # Pagination
    DEFAULT_PAGE_SIZE: int = Field(default=20, ge=1, le=100)
    MAX_PAGE_SIZE: int = Field(default=100, ge=1, le=1000)

    # Rate Limiting (for future use)
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=1)

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: str | PostgresDsn) -> str:
        """Ensure DATABASE_URL uses asyncpg driver."""
        if isinstance(v, str):
            if not v.startswith("postgresql+asyncpg://"):
                # Replace postgresql:// with postgresql+asyncpg://
                if v.startswith("postgresql://"):
                    v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
                else:
                    raise ValueError(
                        "DATABASE_URL must start with 'postgresql://' or 'postgresql+asyncpg://'"
                    )
        return v

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Warn if using default secret key in production."""
        if v == "CHANGE_ME_IN_PRODUCTION_USE_STRONG_SECRET_KEY":
            import warnings

            warnings.warn(
                "Using default SECRET_KEY! Change this in production!",
                UserWarning,
                stacklevel=2,
            )
        return v

    @property
    def database_url_str(self) -> str:
        """Get database URL as string."""
        return str(self.DATABASE_URL)


# Global settings instance
settings = Settings()
