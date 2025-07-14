# ──────────────────────────────────────────────────────────────
#  File: src/adapters/ocr_adapter.py
#  Mac M1 • Python 3.11 • sólo fitz, PIL, pytesseract
# ──────────────────────────────────────────────────────────────

"""Propósito: OCR básico por página usando PyMuPDF + pytesseract

• Renderiza páginas como imagen con fitz (300 DPI)
• Extrae texto con Tesseract OCR
• Utilizado como respaldo para PDFs escaneados

Configuración por defecto:
  - DPI: 300
  - --psm 6 : texto uniforme (ideal para líneas)
  - --oem 1 : motor LSTM (neural net)
  - lang='spa' : idioma español, combinable (ej: 'spa+eng')

Idiomas soportados:
  • eng, spa, fra, deu, ita, por, jpn, chi_sim, chi_tra...
  • Listar con: tesseract --list-langs
  • Instalar con: sudo apt install tesseract-ocr-spa (etc.)

Ejemplo de uso:
  image_to_string(img, lang="spa", config="--psm 6 --oem 1")
"""

from PIL import Image
from io import BytesIO
import cv2
import numpy as np
import logging
import pytesseract
import fitz
import os

# ───────────────────────── Configuración global ─────────────────────────
DPI                 = 600
TESSERACT_CONFIG    = f"--psm 11 --oem 1 -c user_defined_dpi={DPI}"
OCR_LANG            = os.getenv("TESSERACT_LANG", "spa+eng")
TESSERACT_LANG_MODE = os.getenv("TESSERACT_LANG_MODE", "auto")
MIN_W, MIN_H        = 200, 40
OUT_DIR_NAME        = "ocr_tablas_cv"
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

def needs_ocr(page: fitz.Page) -> bool:
    """
    Determina si una página necesita OCR revisando si contiene texto seleccionable.

    Args:
        page (fitz.Page): Página a analizar.

    Returns:
        bool: True si no hay texto y se debe aplicar OCR.
    """
    return page.get_text("text").strip() == ""

def perform_ocr_on_page(page: fitz.Page) -> str:
    """
    Realiza OCR sobre una página de PDF utilizando Tesseract vía pytesseract,
    ajustando automáticamente el modo PSM y el idioma si está activado.

    Args:
        page (fitz.Page): Página de PyMuPDF a procesar.

    Returns:
        str: Texto extraído por OCR.
    """
    pix = page.get_pixmap(dpi=DPI, alpha=False)
    img = Image.open(BytesIO(pix.tobytes("png")))
    img = preprocess_image(img)
    psm = estimate_psm_for_page(img)

    if TESSERACT_LANG_MODE == "auto":
        temp_text = pytesseract.image_to_string(
            img, lang=OCR_LANG, config=f"--psm 11 --oem 1 -c user_defined_dpi={DPI}"
        )
        lang = detect_language(temp_text)
    else:
        lang = OCR_LANG

    config = f"--psm {psm} --oem 1 -c user_defined_dpi={DPI}"
    return pytesseract.image_to_string(img, lang=lang, config=config)

def preprocess_image(img_pil: Image.Image) -> Image.Image:
    """
    Preprocesa la imagen para mejorar la precisión OCR.

    Pasos:
        1. Convierte a escala de grises.
        2. Aplica CLAHE para realzar contraste.
        3. Desenfoque Gaussiano para reducir ruido.
        4. Binariza con umbral adaptativo inverso.

    Args:
        img_pil (Image.Image): Imagen RGB original.

    Returns:
        Image.Image: Imagen binarizada lista para OCR.
    """
    gray = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    blur = cv2.GaussianBlur(enhanced, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 10
    )
    return Image.fromarray(thresh)

def estimate_psm_for_page(img_pil: Image.Image) -> int:
    """
    Estima automáticamente el valor de PSM (Page Segmentation Mode) para Tesseract
    según las características visuales de la imagen renderizada.

    Heurística:
        - Pocas líneas -> PSM 7 (una sola línea)
        - Muchas columnas visibles -> PSM 4 (flujo de columnas)
        - Distribución moderada -> PSM 6 (bloques uniformes)
        - Muy ruidoso o disperso -> PSM 11 (OCR general)

    Args:
        img_pil (Image.Image): Imagen renderizada de la página.

    Returns:
        int: Valor de PSM sugerido.
    """
    img = np.array(img_pil.convert("L"))
    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(255 - binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    num_boxes = len(contours)

    if num_boxes < 5:
        return 7 
    elif num_boxes > 50:
        return 11 
    elif 20 < num_boxes <= 50:
        return 4 
    else:
        return 6 

def detect_language(text: str) -> str:
    """
    Detecta el idioma dominante de un texto para ajustar el parámetro 'lang' de Tesseract.

    Args:
        text (str): Texto plano extraído por OCR preliminar.

    Returns:
        str: Código de idioma compatible con Tesseract (ej. 'spa', 'eng', etc.)
    """
    try:
        from langdetect import detect
        code = detect(text)
        return {
            "es": "spa",
            "en": "eng",
            "fr": "fra",
            "de": "deu",
            "pt": "por"
        }.get(code, "eng")
    except Exception:
        return "eng"