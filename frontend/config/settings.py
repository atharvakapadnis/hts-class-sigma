"""
Configuration settings for Streamlit frontend
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Frontend application settings"""
    
    # API Configuration
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    
    # App Configuration
    APP_TITLE: str = os.getenv("APP_TITLE", "SIGMA Product Catalog")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # UI Configuration
    ITEMS_PER_PAGE: int = int(os.getenv("ITEMS_PER_PAGE", "10"))
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "50"))
    
    # Page Configuration
    PAGE_CONFIG = {
        "page_title": "SIGMA Product Catalog",
        "page_icon": "🔧",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }

settings = Settings()