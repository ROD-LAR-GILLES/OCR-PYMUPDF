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
import pytesseract
import fitz

# ───────────────────────── Configuración global ─────────────────────────
DPI = 300
TESSERACT_CONFIG = f"--psm 6 --oem 1 -c user_defined_dpi={DPI}"
OCR_LANG = "spa"

def perform_ocr_on_page(page: fitz.Page) -> str:
    """
    Realiza OCR sobre una página de PDF utilizando Tesseract vía pytesseract.

    Args:
        page (fitz.Page): Página de PyMuPDF a procesar.

    Returns:
        str: Texto extraído por OCR.
    """
    pix = page.get_pixmap(dpi=DPI, alpha=False)
    img = Image.open(BytesIO(pix.tobytes("png")))
    return pytesseract.image_to_string(img, lang=OCR_LANG, config=TESSERACT_CONFIG)