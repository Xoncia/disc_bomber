from pathlib import Path
from typing import Any

class Config:
    """Application configuration class"""
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    SECRET_KEY = "LKASO92jd890HJAW(*&DHN@#)"
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    @staticmethod
    def get_config_value(key: str) -> Any:
        return getattr(Config, key, None) 