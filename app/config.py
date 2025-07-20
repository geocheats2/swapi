import os
from typing import Any, Dict, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Star Wars API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    TESTING: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite:///./starwars.db"
    
    # External APIs
    SWAPI_BASE_URL: str = "https://swapi.dev/api"
    
    # Security
    SECRET_KEY: str = "change-this-in-production"
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str]) -> str:
        if isinstance(v, str):
            return v
        return "sqlite:///./starwars.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


settings = Settings()
