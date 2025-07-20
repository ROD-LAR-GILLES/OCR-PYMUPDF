"""
Configuración de APIs y credenciales.
Carga variables de entorno de forma robusta usando python-dotenv.
"""
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import os

def load_api_settings() -> dict:
    """
    Carga y valida la configuración de APIs desde variables de entorno.
    Busca el archivo .env en el directorio raíz del proyecto.
    
    Returns:
        dict: Configuración validada de APIs
    """
    # Buscar .env en el directorio raíz del proyecto
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
    
    openai_config = {
        "api_key": openai_key,
        "org_id": os.getenv("OPENAI_ORG_ID"),  # Opcional
        "prompt_model": os.getenv("OPENAI_PROMPT_MODEL", "gpt-3.5-turbo"),
        "ft_model": os.getenv("OPENAI_FT_MODEL"),  # Opcional
    }
    
    return {
        "openai": openai_config
    }
