import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # From .env file
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_CLOUD_LOCATION: str
    STAGING_BUCKET: str
    REVIEW_APP_BASE_URL: str
    REVIEWER_EMAIL: str
    OAUTH_CLIENT_ID: str
    OAUTH_CLIENT_SECRET: str
    AUTH_ID: str

    AGENT_NAME: str

    # Constants
    SCOPES: List[str] = [
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/drive.file",
    ]
    REPORT_CHAR_LIMIT_FOR_REVIEW: int = 500
    COMPETITORS: List[str] = ["comp1", "comp2"]
    REPORT_REVIEW_ID_KEY: str = "report_review_id"
    VERIFICATION_REASONS_KEY: str = "verification_reasons"
    MODEL_NAME: str = "gemini-2.5-flash"  # Default model name for the agent

    # Pydantic V2 configuration
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


def get_settings() -> Settings:
    return Settings()


# Instantiate settings for easy import
settings = get_settings()
