import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = Field(default="Nexus")
    API_STR: str = Field(default="/api/v1")
    MONGODB_URL: str = Field(default="mongodb://localhost:27017")
    DATABASE_NAME: str = Field(default="nexus_db")
    ENVIRONMENT: str = Field(default="development")
    JWT_SECRET_KEY: str = Field(default="supersecretkey") # In production use a strong random string
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)

    # Read from .env file at root first, then look at system env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Instantiate settings as a global singleton
settings = Settings()
