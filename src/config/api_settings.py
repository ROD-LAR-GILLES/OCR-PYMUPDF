"""
API Configuration and Credentials.
Robust environment variable loading using python-dotenv.
Supports multiple LLM providers with fallback options.
"""
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import os

DEFAULT_SETTINGS = {
    "openai": {
        "api_key": None,  # Required
        "org_id": None,   # Optional
        "model_id": "gpt-3.5-turbo",
        "max_retries": 5
    },
    "gemini": {
        "api_key": None,  # Required
        "model_id": "gemini-pro",
        "max_retries": 5
    },
    "deepseek": {
        "api_key": None,  # Required
        "model_id": "deepseek-chat",
        "max_retries": 5,
        "temperature": 0.3
    }
}

def load_api_settings() -> dict:
    """
    Load and validate API settings from environment variables.
    Looks for .env file in project root directory.
    
    Returns:
        dict: Validated API configuration
    """
    # Look for .env in project root
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / ".env"
    
    # Cargar .env si existe
    if env_path.exists():
        load_dotenv(env_path)
    
    # Validar configuración de OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError(
            "OPENAI_API_KEY no encontrada. Asegúrate de tener un archivo .env "
            "en la raíz del proyecto con OPENAI_API_KEY=sk-..."
        )
    
    # Validar configuración de DeepSeek
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    deepseek_config = {
        "api_key": deepseek_key,
        "model_id": os.getenv("DEEPSEEK_MODEL_ID", "deepseek-chat"),
        "temperature": float(os.getenv("DEEPSEEK_TEMPERATURE", "0.3")),
        "max_retries": int(os.getenv("DEEPSEEK_MAX_RETRIES", "5"))
    }

    openai_config = {
        "api_key": openai_key,
        "org_id": os.getenv("OPENAI_ORG_ID"),  # Opcional
        "prompt_model": os.getenv("OPENAI_PROMPT_MODEL", "gpt-3.5-turbo"),
        "ft_model": os.getenv("OPENAI_FT_MODEL"),  # Opcional
    }
    
    return {
        "openai": openai_config
    }
