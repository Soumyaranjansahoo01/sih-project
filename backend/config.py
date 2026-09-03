import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "SIH26027 - Indian Railways Automatic Block Planning"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database
    DATABASE_URL: str = "sqlite:///./backend/railway.db"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"

    # Optimization Configuration
    SOLVER_TIME_LIMIT_SECONDS: int = 60
    DEFAULT_PLANNING_HORIZON_DAYS: int = 7
    MIN_BLOCK_DURATION_MINUTES: int = 60
    MAX_BLOCK_DURATION_MINUTES: int = 240

    # Task Priority Weights (Configurable)
    WEIGHT_CRITICALITY: float = 0.30
    WEIGHT_URGENCY: float = 0.25
    WEIGHT_OVERDUE: float = 0.20
    WEIGHT_ASSET_CONDITION: float = 0.15
    WEIGHT_SAFETY: float = 0.10

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
