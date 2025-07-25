"""
Utilidades para diagnóstico de procesamiento de documentos.

Este módulo proporciona funciones para diagnosticar problemas con el
procesamiento de documentos PDF, incluyendo verificación de permisos,
validación de formato, y diagnóstico de OCR.
"""
import os
import sys
import tempfile
import subprocess
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from loguru import logger

def check_file_permissions(file_path: Path) -> dict:
    """
    Verifica los permisos del archivo.
    
    Args:
        file_path: Ruta al archivo
        
    Returns:
        dict: Información sobre los permisos del archivo
    """
    result = {
        "exists": file_path.exists(),
        "readable": os.access(file_path, os.R_OK),
        "writable": os.access(file_path, os.W_OK),
        "executable": os.access(file_path, os.X_OK),
        "size_bytes": file_path.stat().st_size if file_path.exists() else 0,
        "size_mb": file_path.stat().st_size / (1024 * 1024) if file_path.exists() else 0,
        "owner": get_file_owner(file_path) if file_path.exists() else "N/A",
        "permissions": oct(file_path.stat().st_mode)[-3:] if file_path.exists() else "N/A"
    }
    
    return result

def get_file_owner(file_path: Path) -> str:
    """
    Obtiene el propietario del archivo.
    
    Args:
        file_path: Ruta al archivo
        
    Returns:
        str: Nombre del propietario
    """
    try:
        if sys.platform == "win32":
            # En Windows, es más complejo obtener el propietario
            return "Desconocido (Windows)"
        else:
            # En sistemas Unix, podemos usar stat o subprocess
            import pwd
            stat_info = os.stat(file_path)
            uid = stat_info.st_uid
            user = pwd.getpwuid(uid).pw_name
            return user
    except Exception as e:
        return f"Error al obtener propietario: {e}"

def check_pdf_validity(file_path: Path) -> dict:
    """
    Verifica si el archivo es un PDF válido.
    
    Args:
        file_path: Ruta al archivo
        
    Returns:
        dict: Información sobre la validez del PDF
    """
    result = {
        "is_valid": False,
        "error": None,
        "page_count": 0,
        "version": None,
        "is_encrypted": False,
        "has_text": False,
        "metadata": {}
    }
    
    try:
        with fitz.open(file_path) as doc:
            # PDF básicamente válido si se abre
            result["is_valid"] = True
            result["page_count"] = doc.page_count
            result["version"] = doc.pdf_version
            result["is_encrypted"] = doc.is_encrypted
            
            # Verificar si tiene texto
            has_text = False
            for page in doc:
                if page.get_text().strip():
                    has_text = True
                    break
            result["has_text"] = has_text
            
            # Extraer metadatos básicos
            result["metadata"] = doc.metadata
            
    except Exception as e:
        result["is_valid"] = False
        result["error"] = str(e)
    
    return result

def test_ocr_capability(sample_text="Este es un texto de prueba para OCR") -> dict:
    """
    Prueba la capacidad de OCR generando una imagen con texto y procesándola.
    
    Args:
        sample_text: Texto de muestra para la prueba
        
    Returns:
        dict: Resultados de la prueba de OCR
    """
    result = {
        "ocr_available": False,
        "tesseract_version": None,
        "input_text": sample_text,
        "detected_text": None,
        "accuracy": 0.0,
        "error": None
    }
    
    try:
        # Verificar versión de Tesseract
        result["tesseract_version"] = pytesseract.get_tesseract_version()
        
        # Crear una imagen temporal con el texto
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            temp_img_path = tmp.name
        
        # Generar imagen con texto
        img = Image.new('RGB', (600, 100), color=(255, 255, 255))
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        try:
            # Intentar usar una fuente del sistema
            font = ImageFont.truetype("Arial", 20)
        except:
            # Si no se encuentra, usar la fuente por defecto
            font = ImageFont.load_default()
        
        draw.text((10, 10), sample_text, font=font, fill=(0, 0, 0))
        img.save(temp_img_path)
        
        # Procesar la imagen con OCR
        detected_text = pytesseract.image_to_string(img, lang='spa').strip()
        result["detected_text"] = detected_text
        
        # Calcular precisión simple
        words_input = set(sample_text.lower().split())
        words_detected = set(detected_text.lower().split())
        common_words = words_input.intersection(words_detected)
        
        if words_input:
            result["accuracy"] = len(common_words) / len(words_input) * 100
        
        result["ocr_available"] = True
        
        # Limpiar
        if os.path.exists(temp_img_path):
            os.unlink(temp_img_path)
        
    except Exception as e:
        result["error"] = str(e)
    
    return result

def diagnose_pdf_processing(file_path: Path) -> dict:
    """
    Realiza un diagnóstico completo del procesamiento de un PDF.
    
    Args:
        file_path: Ruta al archivo PDF
        
    Returns:
        dict: Resultados del diagnóstico
    """
    logger.info(f"Iniciando diagnóstico del archivo: {file_path}")
    
    result = {
        "file_info": {},
        "pdf_validity": {},
        "ocr_capability": {},
        "libraries_info": {},
        "system_info": {}
    }
    
    # Verificar permisos y estado del archivo
    result["file_info"] = check_file_permissions(file_path)
    logger.info(f"Información del archivo: {result['file_info']}")
    
    # Si el archivo existe y es legible, verificar validez de PDF
    if result["file_info"]["exists"] and result["file_info"]["readable"]:
        result["pdf_validity"] = check_pdf_validity(file_path)
        logger.info(f"Validez del PDF: {result['pdf_validity']}")
    
    # Probar capacidad de OCR
    result["ocr_capability"] = test_ocr_capability()
    logger.info(f"Capacidad de OCR: {result['ocr_capability']}")
    
    # Información sobre bibliotecas
    result["libraries_info"] = {
        "pymupdf_version": fitz.version,
        "pillow_version": Image.__version__,
        "pytesseract_version": pytesseract.get_tesseract_version() if hasattr(pytesseract, "get_tesseract_version") else "Desconocido"
    }
    logger.info(f"Información de bibliotecas: {result['libraries_info']}")
    
    # Información del sistema
    result["system_info"] = {
        "platform": sys.platform,
        "python_version": sys.version,
        "cwd": os.getcwd()
    }
    logger.info(f"Información del sistema: {result['system_info']}")
    
    return result
