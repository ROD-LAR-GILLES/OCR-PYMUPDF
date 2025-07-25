"""
Función para determinar si una página necesita OCR y para limpiar texto OCR.
"""
from loguru import logger
import fitz
import re
from infrastructure.logging_setup import log_error_details

def needs_ocr(page: fitz.Page) -> bool:
    """
    Determina si una página necesita ser procesada con OCR.
    
    Args:
        page: Página de PyMuPDF
        
    Returns:
        bool: True si la página necesita OCR, False si ya tiene texto extraíble
    """
    try:
        # Extraer texto directamente
        text = page.get_text()
        
        # Criterios para determinar si necesita OCR:
        # 1. No hay texto o muy poco texto
        if len(text.strip()) < 50:
            logger.debug(f"Página {page.number + 1} necesita OCR: texto insuficiente ({len(text)} caracteres)")
            return True
            
        # 2. El texto contiene demasiados caracteres extraños o no válidos
        non_printable = sum(1 for c in text if not c.isprintable() and c not in "\n\t\r ")
        if non_printable > len(text) * 0.2:  # Si más del 20% son caracteres no imprimibles
            logger.debug(f"Página {page.number + 1} necesita OCR: demasiados caracteres no imprimibles ({non_printable}/{len(text)})")
            return True
            
        # 3. Alta proporción de caracteres inusuales o símbolos sospechosos
        unusual_chars = sum(1 for c in text if ord(c) > 127 and not re.match(r'[áéíóúüñÁÉÍÓÚÜÑ¿¡€£]', c))
        if unusual_chars > len(text) * 0.1:  # Si más del 10% son caracteres inusuales
            logger.debug(f"Página {page.number + 1} necesita OCR: caracteres inusuales ({unusual_chars}/{len(text)})")
            return True
            
        # No necesita OCR
        logger.debug(f"Página {page.number + 1} no necesita OCR: texto extraíble de calidad")
        return False
        
    except Exception as e:
        logger.error(f"Error al evaluar si la página {page.number + 1} necesita OCR: {e}")
        log_error_details(e, f"Evaluando OCR para página {page.number + 1}")
        # En caso de error, aplicar OCR por seguridad
        return True

def clean_ocr_text(text: str) -> str:
    """
    Limpia el texto extraído mediante OCR.
    
    Args:
        text: Texto extraído por OCR
        
    Returns:
        str: Texto limpio
    """
    try:
        if not text:
            return ""
            
        # 1. Eliminar caracteres no imprimibles
        text = ''.join(c for c in text if c.isprintable() or c in "\n\t\r ")
        
        # 2. Normalizar espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        
        # 3. Eliminar líneas vacías múltiples
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # 4. Corregir errores comunes de OCR
        text = text.replace('|', 'I').replace('1', 'l', 10)  # No reemplazar todos los '1' por 'l'
        
        # 5. Eliminar guiones de continuación a final de línea 
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2\n', text)
        
        # 6. Eliminar marcas de agua o textos repetitivos típicos
        repetitive_patterns = [
            r'Documento\s+[gG]enerado.*?\n',
            r'[Pp]ágina\s+\d+\s+de\s+\d+',
            r'www\..*?\.com',
            r'©.*?[Rr]eservados'
        ]
        for pattern in repetitive_patterns:
            text = re.sub(pattern, '', text)
            
        return text.strip()
        
    except Exception as e:
        logger.error(f"Error al limpiar texto OCR: {e}")
        log_error_details(e, "Limpieza de texto OCR")
        # En caso de error, devolver el texto original
        return text

def apply_corrections(text: str) -> str:
    """
    Aplica correcciones específicas al texto extraído.
    
    Args:
        text: Texto extraído por OCR
        
    Returns:
        str: Texto corregido
    """
    try:
        if not text:
            return ""
            
        # Diccionario básico de correcciones comunes en español legal
        corrections = {
            'Articulo': 'Artículo',
            'articulo': 'artículo',
            'parrafo': 'párrafo',
            'Parrafo': 'Párrafo',
            'Codigo': 'Código',
            'codigo': 'código',
            'Clausula': 'Cláusula',
            'clausula': 'cláusula',
            'termino': 'término',
            'Termino': 'Término',
            'resolucion': 'resolución',
            'Resolucion': 'Resolución',
            'Asi': 'Así',
            'segun': 'según'
        }
        
        # Aplicar correcciones
        for wrong, correct in corrections.items():
            # Usar regex para asegurar que son palabras completas
            text = re.sub(r'\b' + wrong + r'\b', correct, text)
            
        return text
        
    except Exception as e:
        logger.warning(f"Error al aplicar correcciones: {e}")
        # En caso de error, devolver el texto original
        return text
