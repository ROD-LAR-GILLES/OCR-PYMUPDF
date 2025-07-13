"""
Adaptador para realizar OCR sobre páginas de PDF utilizando Tesseract.

Este módulo convierte páginas de PyMuPDF en imágenes y extrae texto usando pytesseract.
"""

from PIL import Image
from io import BytesIO
import pytesseract
import fitz

def perform_ocr_on_page(page: fitz.Page) -> str:
    """
    Realiza OCR sobre una página del PDF y devuelve texto plano.

    Args:
        page (fitz.Page): Página de PyMuPDF.

    Returns:
        str: Texto extraído por OCR.
    """
    pix = page.get_pixmap(dpi=300, alpha=False)
    img = Image.open(BytesIO(pix.tobytes("png")))
    return pytesseract.image_to_string(img)