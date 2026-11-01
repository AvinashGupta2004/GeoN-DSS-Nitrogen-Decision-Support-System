"""
Application configuration — reads from .env
"""
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List

ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_PORT: int = 8000
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]

    GEE_SERVICE_ACCOUNT: str = ""
    GEE_KEY_FILE: str = ""

    CLASSIFIER_MODEL_PATH: str = str(ROOT_DIR / "ml" / "saved_models" / "lgbm_classifier.joblib")
    REGRESSOR_MODEL_PATH: str = str(ROOT_DIR / "ml" / "saved_models" / "xgb_regressor.joblib")

    class Config:
        env_file = ".env"


settings = Settings()
