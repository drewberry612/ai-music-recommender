from pydantic import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    LOG_DIR: Path = Path("logs/")
    LOG_UPLOAD_INTERVAL_MINS: int = 30  # Interval to upload logs
    GOOGLE_DRIVE_FOLDER_ID: str  # Must be set via environment or .env file
    CREDENTIALS_PATH: Path = Path("credentials.json")  # Google service account creds

    class Config:
        env_file = ".env"

settings = Settings()