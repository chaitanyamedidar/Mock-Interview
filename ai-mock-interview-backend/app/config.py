import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """
    Centralized configuration for AI Mock Interview Platform.
    Manages GCP Gemini (primary) and OpenRouter (fallback) settings.
    """
    
    # GCP Gemini API (Primary)
    google_ai_api_key: str
    gemini_model: str = "gemini-2.5-flash"
    gemini_temperature: float = 0.3
    gemini_max_tokens: int = 2048
    gemini_top_p: float = 0.95
    gemini_top_k: int = 40
    
    # OpenRouter (Fallback)
    llm_api_key: Optional[str] = None
    llm_base_url: str = "https://openrouter.ai/api/v1"
    llm_model: str = "google/gemini-2.0-flash-exp:free"
    
    # Database
    database_url: str = "sqlite:///./interview_platform.db"
    
    # VAPI
    vapi_api_key: Optional[str] = None
    vapi_webhook_secret: Optional[str] = None
    backend_url: str = "http://localhost:8000"
    
    # Application
    debug: bool = False
    secret_key: str = "your_secret_key_for_jwt_tokens_here"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
        # Map environment variables to field names
        fields = {
            'google_ai_api_key': {'env': 'GOOGLE_AI_API_KEY'},
            'gemini_model': {'env': 'GEMINI_MODEL'},
            'gemini_temperature': {'env': 'GEMINI_TEMPERATURE'},
            'gemini_max_tokens': {'env': 'GEMINI_MAX_TOKENS'},
            'gemini_top_p': {'env': 'GEMINI_TOP_P'},
            'gemini_top_k': {'env': 'GEMINI_TOP_K'},
            'llm_api_key': {'env': 'LLM_API_KEY'},
            'llm_base_url': {'env': 'LLM_BASE_URL'},
            'llm_model': {'env': 'LLM_MODEL'},
            'database_url': {'env': 'DATABASE_URL'},
            'vapi_api_key': {'env': 'VAPI_API_KEY'},
            'vapi_webhook_secret': {'env': 'VAPI_WEBHOOK_SECRET'},
            'backend_url': {'env': 'BACKEND_URL'},
            'debug': {'env': 'DEBUG'},
            'secret_key': {'env': 'SECRET_KEY'},
        }

# Global settings instance
settings = Settings()

# Validate critical settings
if not settings.google_ai_api_key:
    import logging
    logging.warning("GOOGLE_AI_API_KEY not set. GCP Gemini will not be available.")

if not settings.llm_api_key:
    import logging
    logging.warning("LLM_API_KEY not set. OpenRouter fallback will not be available.")
