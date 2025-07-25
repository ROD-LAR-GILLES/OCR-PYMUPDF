"""
Validación de claves de API para proveedores LLM.

Este módulo verifica la presencia de las claves de API necesarias
para los diferentes proveedores de LLM y advierte cuando faltan.
"""
import os
import logging

# Configurar logger
logger = logging.getLogger(__name__)

# Claves requeridas para los diferentes proveedores LLM
REQUIRED_LLM_KEYS = ["OPENAI_API_KEY"]
OPTIONAL_LLM_KEYS = ["GEMINI_API_KEY", "DEEPSEEK_API_KEY", "ANTHROPIC_API_KEY"]

def check_llm_keys(strict: bool = False) -> dict:
    """
    Verifica la presencia de claves de API para proveedores LLM.
    
    Args:
        strict: Si es True, lanza una excepción cuando faltan claves requeridas.
              Si es False, solo registra una advertencia.
              
    Returns:
        dict: Un diccionario con el estado de las claves (True/False)
    """
    # Verificar claves requeridas
    missing_required = [k for k in REQUIRED_LLM_KEYS if not os.getenv(k)]
    
    # Verificar claves opcionales
    available_optional = {k: bool(os.getenv(k)) for k in OPTIONAL_LLM_KEYS}
    
    # Crear resumen de estado
    status = {
        "required_complete": len(missing_required) == 0,
        "available_providers": {k: bool(os.getenv(k)) for k in REQUIRED_LLM_KEYS + OPTIONAL_LLM_KEYS if os.getenv(k)},
        "missing_required": missing_required,
        "available_optional": available_optional
    }
    
    # Registrar resultado
    if missing_required:
        msg = f"No se encontraron claves de API para los proveedores LLM requeridos: {missing_required}"
        if strict:
            logger.error(msg)
            raise RuntimeError(msg)
        else:
            logger.warning(msg)
    
    # Registrar proveedores disponibles
    if status["available_providers"]:
        logger.info(f"Proveedores LLM disponibles: {list(status['available_providers'].keys())}")
    else:
        logger.warning("No hay proveedores LLM disponibles. El refinamiento LLM estará desactivado.")
    
    return status

def get_available_llm_provider():
    """
    Obtiene el primer proveedor LLM disponible según el orden de prioridad.
    
    Returns:
        str or None: Nombre del proveedor LLM disponible, o None si no hay ninguno.
    """
    # Orden de prioridad para proveedores
    priority_order = REQUIRED_LLM_KEYS + OPTIONAL_LLM_KEYS
    
    # Verificar cada proveedor en orden
    for provider_key in priority_order:
        if os.getenv(provider_key):
            # Extraer nombre del proveedor (ej: OPENAI_API_KEY -> openai)
            provider_name = provider_key.split('_')[0].lower()
            return provider_name
    
    return None

def get_available_llm_providers():
    """
    Obtiene todos los proveedores LLM disponibles.
    
    Returns:
        list: Lista de nombres de proveedores LLM disponibles.
    """
    available_providers = []
    all_provider_keys = REQUIRED_LLM_KEYS + OPTIONAL_LLM_KEYS
    
    for provider_key in all_provider_keys:
        if os.getenv(provider_key):
            # Extraer nombre del proveedor (ej: OPENAI_API_KEY -> openai)
            provider_name = provider_key.split('_')[0].lower()
            available_providers.append(provider_name)
    
    return available_providers
