"""
Módulo para verificar las claves de API de proveedores LLM.

Verifica si las variables de entorno necesarias para los distintos
proveedores de LLM están disponibles, y emite advertencias
o errores según corresponda.
"""
import os
from typing import List, Dict
from loguru import logger

# Claves requeridas por cada proveedor
REQUIRED_LLM_KEYS: Dict[str, List[str]] = {
    "openai": ["OPENAI_API_KEY"],
    "anthropic": ["ANTHROPIC_API_KEY"],
    "gemini": ["GEMINI_API_KEY"],
    "deepseek": ["DEEPSEEK_API_KEY"]
}

def check_llm_keys(strict: bool = False) -> Dict[str, bool]:
    """
    Verifica la presencia de claves de API para proveedores LLM.
    
    Args:
        strict: Si es True, lanza una excepción cuando faltan claves.
              Si es False, solo emite advertencias.
              
    Returns:
        Diccionario con el estado de disponibilidad de cada proveedor.
        
    Raises:
        RuntimeError: Si strict=True y falta alguna clave requerida.
    """
    provider_status = {}
    missing_keys = []
    
    # Verificar cada proveedor
    for provider, keys in REQUIRED_LLM_KEYS.items():
        missing_provider_keys = [k for k in keys if not os.getenv(k)]
        provider_status[provider] = len(missing_provider_keys) == 0
        
        if missing_provider_keys:
            missing_keys.extend(missing_provider_keys)
            logger.warning(f"No se encontraron claves de API para {provider}: {missing_provider_keys}")
    
    # Si no hay ningún proveedor disponible, mostrar una advertencia más clara
    if not any(provider_status.values()):
        msg = f"No se encontraron claves de API para ningún proveedor LLM: {missing_keys}"
        logger.warning(msg)
        if strict:
            raise RuntimeError(msg)
    
    return provider_status

def get_available_llm_providers() -> List[str]:
    """
    Obtiene la lista de proveedores LLM disponibles según las claves configuradas.
    
    Returns:
        Lista de nombres de proveedores disponibles.
    """
    provider_status = check_llm_keys(strict=False)
    return [provider for provider, available in provider_status.items() if available]
