"""Adaptador para extracción con PyMuPDF4LLM y OCR fallback."""
from pathlib import Path
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from io import BytesIO
from pymupdf4llm import to_markdown
from loguru import logger


def _is_scanned(pdf_path: Path) -> bool:
    """Determina si la primera página no contiene texto seleccionable."""
    with fitz.open(pdf_path) as doc:
        page = doc[0]
        return page.get_text("text").strip() == ""


def _ocr_first_page(page) -> str:
    """Realiza OCR sobre la primera página y devuelve texto plano."""
    pix = page.get_pixmap(dpi=300, alpha=False)
    img = Image.open(BytesIO(pix.tobytes("png")))
    return pytesseract.image_to_string(img)


def extract_markdown(pdf_path: Path) -> str:
    """Devuelve Markdown, usando OCR si es un PDF escaneado."""
    pdf_path = Path(pdf_path)
    if _is_scanned(pdf_path):
        logger.warning("PDF detectado como escaneado, usando OCR.")
        with fitz.open(pdf_path) as doc:
            text = _ocr_first_page(doc[0])
        # Aquí generamos un Markdown mínimo
        return f"# {pdf_path.stem}\n\n{text}"
    logger.info("PDF digital detectado, usando PyMuPDF4LLM.")
    return to_markdown(path=str(pdf_path))