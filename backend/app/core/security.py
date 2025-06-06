"""
Security utilities and dependencies
"""

from fastapi import HTTPException, status
from app.core.config import settings

def verify_api_key(api_key: str) -> bool:
    """Verify API key (placeholder for future authentication)"""
    # For now, just check if OpenAI key is configured
    return bool(settings.OPENAI_API_KEY)


def get_openai_client():
    """Get configured OpenAI client"""
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key not configured"
        )
    
    try:
        from openai import OpenAI
        return OpenAI(api_key=settings.OPENAI_API_KEY)
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI library not installed"
        )