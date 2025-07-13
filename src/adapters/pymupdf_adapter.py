"""
Adaptador para extracción de contenido de archivos PDF a formato Markdown, utilizando PyMuPDF4LLM para PDFs digitales
y OCR (Tesseract) como mecanismo de respaldo en caso de PDFs escaneados (sin texto seleccionable).

Este módulo cumple la función de adaptador dentro de la arquitectura limpia, delegando la lógica de extracción de texto
a herramientas externas y encapsulando la decisión sobre el método adecuado de procesamiento.
"""
from pathlib import Path
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from io import BytesIO
from pymupdf4llm import to_markdown
from loguru import logger
from adapters.ocr_adapter import perform_ocr_on_page


def _is_scanned(pdf_path: Path) -> bool:
    """
    Determina si un archivo PDF es escaneado, verificando si la primera página contiene texto seleccionable.

    Args:
        pdf_path (Path): Ruta al archivo PDF.

    Returns:
        bool: True si no hay texto seleccionable en la primera página, False en caso contrario.
    """
    with fitz.open(pdf_path) as doc:
        page = doc[0]
        return page.get_text("text").strip() == ""

def extract_markdown(pdf_path: Path) -> str:
    """
    Extrae el contenido de un archivo PDF en formato Markdown. Usa OCR si se detecta que el PDF es escaneado.

    Args:
        pdf_path (Path): Ruta al archivo PDF.

    Returns:
        str: Contenido en formato Markdown.
    """
    pdf_path = Path(pdf_path)
    with fitz.open(pdf_path) as doc:
        if _is_scanned(pdf_path):
            logger.warning("PDF detectado como escaneado, usando OCR en todas las páginas.")
            ocr_text = []
            for i, page in enumerate(doc):
                logger.info(f"Procesando OCR página {i + 1}")
                text = perform_ocr_on_page(page)
                ocr_text.append(f"## Página {i + 1}\n\n{text.strip()}")
            full_markdown = f"# {pdf_path.stem}\n\n" + "\n\n".join(ocr_text)
            return full_markdown
        else:
            logger.info("PDF digital detectado, usando PyMuPDF4LLM.")
            return to_markdown(str(pdf_path))