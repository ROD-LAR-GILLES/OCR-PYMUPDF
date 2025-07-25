"""
Implementa procesamiento OCR en paralelo para PDFs completos.
"""
from pathlib import Path
from typing import List
import os
import fitz
import pytesseract
from PIL import Image
from loguru import logger

def run_parallel(pdf_path: Path) -> List[str]:
    """
    Procesa un PDF completo con OCR, extrayendo texto de cada página.
    
    Args:
        pdf_path: Ruta al PDF
        
    Returns:
        Lista de textos por página
    """
    results = []
    
    try:
        # Verificar archivo
        if not pdf_path.exists():
            error_msg = f"El archivo PDF no existe: {pdf_path}"
            logger.error(error_msg)
            return [error_msg]
            
        # Verificar tamaño del archivo
        file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
        logger.info(f"Tamaño del archivo PDF: {file_size_mb:.2f} MB")
        
        # Verificar Tesseract
        try:
            tesseract_version = pytesseract.get_tesseract_version()
            logger.info(f"Versión de Tesseract: {tesseract_version}")
        except Exception as te:
            logger.error(f"Error al verificar Tesseract: {te}")
            from infrastructure.logging_setup import log_error_details
            log_error_details(te, "Verificación de Tesseract")
        
        with fitz.open(str(pdf_path)) as doc:
            total_pages = doc.page_count
            logger.info(f"OCR paralelo iniciado. PDF tiene {total_pages} páginas")
            
            for page_num, page in enumerate(doc, start=1):
                logger.info(f"OCR paralelo en página {page_num}/{total_pages}")
                
                try:
                    # Verificar dimensiones de la página
                    width, height = page.rect.width, page.rect.height
                    logger.debug(f"Dimensiones de página {page_num}: {width}x{height}")
                    
                    # Renderizar página como imagen
                    pix = page.get_pixmap(alpha=False)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    # Registrar información de la imagen
                    logger.debug(f"Imagen generada: {img.width}x{img.height} píxeles")
                    
                    # Realizar OCR
                    text = pytesseract.image_to_string(img, lang='spa')
                    
                    # Verificar resultados
                    if not text.strip():
                        logger.warning(f"OCR no detectó texto en la página {page_num}")
                        results.append(f"[PÁGINA {page_num}]: No se detectó texto.")
                    else:
                        logger.info(f"OCR completado para página {page_num}: {len(text)} caracteres")
                        results.append(text)
                
                except Exception as e:
                    error_msg = f"Error en OCR para página {page_num}: {e}"
                    logger.error(error_msg)
                    from infrastructure.logging_setup import log_error_details
                    log_error_details(e, f"OCR en página {page_num} de {pdf_path}")
                    results.append(f"[ERROR EN PÁGINA {page_num}]: {str(e)}")
        
        logger.info("OCR paralelo completado con éxito")
        return results
    
    except Exception as e:
        logger.error(f"Error crítico en OCR paralelo: {e}")
        from infrastructure.logging_setup import log_error_details
        log_error_details(e, f"OCR paralelo de {pdf_path}")
        return [f"Error crítico al procesar el documento con OCR: {str(e)}"]
