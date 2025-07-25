# ──────────────────────────────────────────────────────────────
#  File: src/adapters/out/ocr/ocr_adapter.py
#  Python 3.11 • OCR functionality for PDF processing
# ──────────────────────────────────────────────────────────────

"""
OCR Adapter para procesamiento de texto en PDFs escaneados.

Proporciona funcionalidades de OCR usando PyMuPDF + Tesseract:
- Renderiza páginas como imagen de alta resolución
- Extrae texto con Tesseract OCR
- Utilizado como respaldo para PDFs escaneados

Configuración por defecto:
  - DPI: 300
  - PSM 6: texto uniforme (ideal para líneas)
  - OEM 1: motor LSTM (neural net)
  - lang='spa': idioma español

Idiomas soportados:
  - eng, spa, fra, deu, ita, por, jpn, chi_sim, chi_tra...
  - Listar con: tesseract --list-langs
  - Instalar con: sudo apt install tesseract-ocr-spa (etc.)
"""

import logging
import os
import re
import unicodedata
from io import BytesIO
from pathlib import Path
import fitz
from PIL import Image

# Configuración global
DPI = 300
OCR_LANG = "spa"

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
    Realiza OCR sobre una página PDF usando Tesseract.
    
    Args:
        page: Página PDF de PyMuPDF

    Returns:
        str: Texto extraído y procesado
    """
    try:
        # Primero intentar extraer texto directamente
        direct_text = page.get_text().strip()
        
        # Si ya hay texto extraíble y es de buena calidad, usarlo
        if direct_text and len(direct_text) > 50:
            alphabetic_chars = sum(1 for c in direct_text if c.isalpha())
            total_chars = len(direct_text.replace(' ', '').replace('\n', ''))
            
            if total_chars > 0:
                alphabetic_ratio = alphabetic_chars / total_chars
                if alphabetic_ratio > 0.7:  # Buen texto extraíble
                    return clean_ocr_text(direct_text)
        
        # Si el texto directo no es suficiente, realizar OCR
        return _perform_tesseract_ocr(page)
        
    except Exception as e:
        logging.error(f"Error en OCR para página {page.number + 1}: {e}")
        return f"[ERROR DE OCR EN PÁGINA {page.number + 1}]"


def _perform_tesseract_ocr(page: fitz.Page) -> str:
    """
    Ejecuta OCR con Tesseract en una página.
    
    Args:
        page: Página PDF de PyMuPDF
        
    Returns:
        str: Texto extraído con OCR
    """
    try:
        # Renderizar página como imagen
        pix = page.get_pixmap(dpi=DPI, alpha=False)
        img_data = pix.tobytes("png")
        img = Image.open(BytesIO(img_data))
        
        # OCR básico (requiere pytesseract instalado)
        try:
            import pytesseract
            config = f"--psm 6 --oem 1 -c user_defined_dpi={DPI}"
            text = pytesseract.image_to_string(img, lang=OCR_LANG, config=config)
            
            if not text.strip():
                # Intentar con configuración alternativa
                config_alt = f"--psm 3 --oem 1 -c user_defined_dpi={DPI}"
                text = pytesseract.image_to_string(img, lang=OCR_LANG, config=config_alt)
                
        except ImportError:
            logging.warning("pytesseract no está instalado. Devolviendo texto básico.")
            return f"[OCR NO DISPONIBLE - PÁGINA {page.number + 1}]"
        except Exception as e:
            logging.error(f"Error en Tesseract OCR: {e}")
            return f"[ERROR DE TESSERACT EN PÁGINA {page.number + 1}]"
        
        # Limpiar y procesar el texto
        return clean_ocr_text(text)
        
    except Exception as e:
        logging.error(f"Error en OCR Tesseract para página {page.number + 1}: {e}")
        return f"[ERROR CRÍTICO DE OCR EN PÁGINA {page.number + 1}]"


def clean_ocr_text(text: str) -> str:
    """
    Limpia y normaliza el texto extraído por OCR.
    
    Args:
        text: Texto bruto de OCR
        
    Returns:
        str: Texto limpio y normalizado
    """
    if not text:
        return ""
        
    try:
        # Normalización Unicode
        text = unicodedata.normalize("NFKC", text)
        
        # Eliminar caracteres no imprimibles manteniendo acentos españoles
        text = re.sub(r"[^\w\sÁÉÍÓÚÜÑñáéíóúü¿¡.,;:%\-()/]", " ", text)
        
        # Colapsar espacios múltiples
        text = re.sub(r"\s{2,}", " ", text)
        
        # Eliminar líneas con muy poco contenido alfabético
        lines = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
                
            # Calcular ratio de caracteres alfabéticos
            alphabetic_chars = sum(1 for c in line if c.isalpha())
            total_chars = len(line)
            
            if total_chars > 0:
                alphabetic_ratio = alphabetic_chars / total_chars
                if alphabetic_ratio >= 0.3:  # Al menos 30% caracteres alfabéticos
                    lines.append(line)
        
        return "\n".join(lines)
        
    except Exception as e:
        logging.error(f"Error limpiando texto OCR: {e}")
        return text  # Devolver texto original si falla la limpieza


def apply_corrections(text: str) -> str:
    """
    Aplica correcciones manuales comunes de OCR.
    
    Args:
        text: Texto a corregir
        
    Returns:
        str: Texto con correcciones aplicadas
    """
    if not text:
        return text
        
    try:
        # Correcciones comunes de OCR
        corrections = {
            r'\brn\b': 'm',  # rn -> m
            r'\bIl\b': 'II',  # Il -> II (números romanos)
            r'\b0\b': 'O',   # 0 -> O en algunos contextos
            r'\bl\b': 'I',   # l -> I en números romanos
        }
        
        for pattern, replacement in corrections.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            
        return text
        
    except Exception as e:
        logging.error(f"Error aplicando correcciones: {e}")
        return text


# Funciones adicionales para compatibilidad
def detect_table_regions(img):
    """Stub para detección de tablas"""
    return []


def ocr_table_to_markdown(img) -> str:
    """Stub para OCR de tablas"""
    return ""


def detect_lists(text: str) -> str:
    """
    Detecta y formatea listas en texto.
    
    Args:
        text: Texto plano
        
    Returns:
        str: Texto con formato de lista en Markdown
    """
    if not text:
        return text
        
    lines = text.splitlines()
    output = []
    
    for line in lines:
        line = line.strip()
        
        # Lista numerada
        if re.match(r"^\(?\d+[\.\)-]", line):
            line = re.sub(r"^\(?(\d+)[\.\)-]\s*", r"\1. ", line)
        # Lista con viñetas
        elif re.match(r"^[-•–]", line):
            line = re.sub(r"^[-•–]\s*", "- ", line)
            
        output.append(line)
    
    return "\n".join(output)


def apply_manual_corrections(text: str) -> str:
    """
    Aplica correcciones desde archivo CSV si existe.
    
    Args:
        text: Texto a corregir
        
    Returns:
        str: Texto corregido
    """
    corrections_path = Path("data/corrections.csv")
    
    if not corrections_path.exists():
        return text
        
    try:
        import csv
        with corrections_path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                if "ocr" in row and "correct" in row:
                    bad, good = row["ocr"], row["correct"]
                    # Reemplazo como palabra completa
                    text = re.sub(rf"\b{re.escape(bad)}\b", good, text, flags=re.IGNORECASE)
    except Exception as e:
        logging.error(f"Error aplicando correcciones manuales: {e}")
        
    return text
