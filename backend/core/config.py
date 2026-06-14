"""
config.py
Loads environment variables and defines settings for the application.
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load explicitly if .env exists
load_dotenv()

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "AI Job Copilot"
    API_V1_STR: str = ""
    FRONTEND_URL: str = "http://localhost:5173"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret_key")

    # MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = "ai_job_copilot"

    # JWT Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev_jwt_secret_key_minimum_32_chars")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Third Party APIs
    OPENROUTER_API_KEY: str = ""
    TAVILY_API_KEY: str = ""

    # LLM model names (via OpenRouter)
    # Writer: reasoning + writing tasks (research, cover letter, interview prep, outreach, supervisor)
    LLM_WRITER_MODEL: str = "openrouter/auto"
    # Coder: structured transformation tasks (resume rewriting)
    LLM_CODER_MODEL: str = "openrouter/auto"

    # Uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # SMTP (Email Outreach)
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")

    # Ensure upload dir exists
    def create_dirs(self):
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
settings.create_dirs()
