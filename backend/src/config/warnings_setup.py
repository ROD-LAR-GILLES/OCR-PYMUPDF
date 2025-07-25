"""
Módulo para configurar filtros de advertencias.

Este módulo configura filtros para silenciar advertencias específicas
que no son críticas para el funcionamiento de la aplicación.
"""
import warnings
import logging

logger = logging.getLogger(__name__)

def configure_warnings():
    """
    Configura filtros para silenciar advertencias específicas.
    
    Esta función debe ser llamada al inicio de la aplicación,
    antes de que se importen módulos que puedan generar las advertencias.
    """
    # Silenciar advertencias de deprecación de ARC4 en cryptography
    try:
        from cryptography.utils import CryptographyDeprecationWarning
        warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)
        logger.debug("Filtro configurado para CryptographyDeprecationWarning")
    except ImportError:
        logger.debug("No se pudo importar CryptographyDeprecationWarning, saltando filtro")
    
    # Silenciar advertencias de PyMuPDF sobre versión de xref
    warnings.filterwarnings("ignore", message="startxref not found")
    
    # Silenciar advertencias comunes de numpy en procesamiento de imágenes
    warnings.filterwarnings("ignore", message="numpy.dtype size changed")
    warnings.filterwarnings("ignore", message="numpy.ufunc size changed")
    
    logger.debug("Filtros de advertencias configurados correctamente")
