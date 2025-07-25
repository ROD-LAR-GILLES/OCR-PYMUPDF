"""
Configuración de filtros para advertencias del sistema.

Este módulo configura filtros para silenciar advertencias específicas,
como las relacionadas con CryptographyDeprecationWarning para ARC4.
"""
import warnings
import logging

logger = logging.getLogger(__name__)

def configure_warnings():
    """
    Configura los filtros de advertencias para silenciar advertencias específicas.
    
    Esta función debe ser llamada temprano en la inicialización de la aplicación,
    preferiblemente antes de importar cualquier módulo que pueda generar advertencias.
    """
    # Silenciar advertencias específicas
    try:
        # Silenciar advertencias de CryptographyDeprecationWarning
        from cryptography.utils import CryptographyDeprecationWarning
        warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)
        logger.debug("Configurados filtros para CryptographyDeprecationWarning")
    except ImportError:
        logger.debug("No se pudo importar CryptographyDeprecationWarning")
    
    # Configurar otros filtros según sea necesario
    # warnings.filterwarnings("ignore", message=".*some specific message.*")
    
    logger.info("Filtros de advertencias configurados correctamente")
