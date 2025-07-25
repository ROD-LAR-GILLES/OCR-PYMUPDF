"""
Módulo OCR simple para corregir errores de import.
"""

import fitz

def needs_ocr(page: fitz.Page) -> bool:
    """
    Determina si una página necesita OCR basándose en la cantidad de texto extraíble.
    
    Args:
        page: Página de PyMuPDF
        
    Returns:
        bool: True si necesita OCR, False si tiene texto extraíble
    """
    try:
        # Extraer texto directamente
        text = page.get_text().strip()
        
        # Si no hay texto o es muy poco, necesita OCR
        if not text or len(text) < 10:
            return True
            
        # Si la mayoría son caracteres no alfabéticos, probablemente es texto escaneado mal reconocido
        alphabetic_chars = sum(1 for c in text if c.isalpha())
        total_chars = len(text.replace(' ', '').replace('\n', ''))
        
        if total_chars == 0:
            return True
            
        alphabetic_ratio = alphabetic_chars / total_chars
        
        # Si menos del 60% son caracteres alfabéticos, probablemente necesita OCR
        return alphabetic_ratio < 0.6
        
    except Exception:
        # En caso de error, asumir que necesita OCR
        return True


def perform_ocr_on_page(page: fitz.Page) -> str:
    """
    Función stub para realizar OCR en una página.
    Por ahora retorna el texto que se puede extraer directamente.
    """
    try:
        return page.get_text()
    except Exception:
        return ""
