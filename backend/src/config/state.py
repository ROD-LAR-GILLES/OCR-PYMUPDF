# src/config/state.py
import os
from dotenv import load_dotenv
from infrastructure.logging_setup import logger

"""
Estado global compartido para el modo LLM.

Valores posibles:
    • "off"    → desactiva LLM
    • "prompt" → usa prompt directo
"""

def load_configuration():
    """Carga la configuración desde variables de entorno."""
    # Cargar variables de entorno desde .env
    load_dotenv()
    
    # Verificar configuración LLM
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        logger.warning("No se encontraron claves de API para los proveedores LLM")
        return "off"
    
    return "prompt"

# Se ejecuta una sola vez al importar `config.state`
LLM_MODE = load_configuration()