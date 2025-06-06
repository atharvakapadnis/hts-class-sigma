"""
Configuration settings for APP
"""

from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from env variables"""

    # API Config
    PROJECT_NAME: str = "HTS-Class_SIGMA"
    PROJECT_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # OPENAI API Config
    OPENAI_API_KEY: str = ""

    # CORS Config
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:5173"
    ]

    # Data file paths
    DATA_DIR: str = "app/data"
    PRODUCTS_FILE: str = "ductile_iron_fittings.json"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()