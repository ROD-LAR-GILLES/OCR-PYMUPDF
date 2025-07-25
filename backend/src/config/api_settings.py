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
        dict: Validated API configuration with available providers
    """
    from infrastructure.logging_setup import logger
    
    # Look for .env in project root and load it
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / ".env"
    
    # Cargar .env si existe
    if env_path.exists():
        logger.debug(f"Loading environment from {env_path}")
        load_dotenv(str(env_path), override=True)  # Asegurar que se sobreescriban las variables existentes
        logger.debug("Environment variables loaded successfully")
    else:
        logger.warning(f"No .env file found at {env_path}")
        
    # Debug de las variables cargadas
    env_vars = {
        "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
        "OPENAI_MODEL_ID": os.getenv("OPENAI_MODEL_ID"),
        "GEMINI_API_KEY": bool(os.getenv("GEMINI_API_KEY")),
        "GEMINI_MODEL_ID": os.getenv("GEMINI_MODEL_ID"),
        "DEEPSEEK_API_KEY": bool(os.getenv("DEEPSEEK_API_KEY")),
        "DEEPSEEK_MODEL_ID": os.getenv("DEEPSEEK_MODEL_ID")
    }
    logger.debug(f"Loaded environment variables: {env_vars}")
    
    config = {}
    
    # Configuración de OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        config["openai"] = {
            "api_key": openai_key,
            "org_id": os.getenv("OPENAI_ORG_ID"),
            "model_id": os.getenv("OPENAI_MODEL_ID", "gpt-3.5-turbo"),
            "max_retries": int(os.getenv("OPENAI_MAX_RETRIES", "5"))
        }
    
    # Configuración de Gemini
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        config["gemini"] = {
            "api_key": gemini_key,
            "model_id": os.getenv("GEMINI_MODEL_ID", "gemini-pro"),
            "max_retries": int(os.getenv("GEMINI_MAX_RETRIES", "5"))
        }
    
    # Configuración de DeepSeek
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key:
        config["deepseek"] = {
            "api_key": deepseek_key,
            "model_id": os.getenv("DEEPSEEK_MODEL_ID", "deepseek-chat"),
            "temperature": float(os.getenv("DEEPSEEK_TEMPERATURE", "0.3")),
            "max_retries": int(os.getenv("DEEPSEEK_MAX_RETRIES", "5"))
        }
    
    logger.debug(f"Loaded API configurations: {list(config.keys())}")
    for provider, cfg in config.items():
        masked_key = cfg.get("api_key", "")[:10] + "..." if cfg.get("api_key") else "None"
        logger.debug(f"{provider} config: api_key={masked_key}, model={cfg.get('model_id')}")
    
    return config
