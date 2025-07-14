"""
Adaptador para extracción de contenido de archivos PDF a formato Markdown, utilizando PyMuPDF4LLM para PDFs digitales
y OCR (Tesseract) como mecanismo de respaldo en caso de PDFs escaneados (sin texto seleccionable).

Este módulo cumple la función de adaptador dentro de la arquitectura limpia, delegando la lógica de extracción de texto
a herramientas externas y encapsulando la decisión sobre el método adecuado de procesamiento.
"""
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
from pymupdf4llm import to_markdown
from loguru import logger
from adapters.ocr_adapter import perform_ocr_on_page



def extract_markdown(pdf_path: Path) -> str:
    """
    Extrae el contenido de un archivo PDF en formato Markdown. Usa OCR si se detecta que una página no contiene texto.

    Args:
        pdf_path (Path): Ruta al archivo PDF.

    Returns:
        str: Contenido en formato Markdown.
    """
    from adapters.ocr_adapter import needs_ocr

    logger.info("Iniciando análisis de páginas individuales para aplicar OCR selectivo si es necesario.")

    with fitz.open(pdf_path) as doc:
        ocr_text = []
        for i, page in enumerate(doc):
            if needs_ocr(page):
                logger.info(f"[Página {i + 1}] Sin texto detectable. Aplicando OCR...")
                text = perform_ocr_on_page(page)
            else:
                logger.info(f"[Página {i + 1}] Texto detectado. Extrayendo directamente...")
                text = page.get_text("text")
            ocr_text.append(f"## Página {i + 1}\n\n{text.strip()}")

    full_markdown = f"# {pdf_path.stem}\n\n" + "\n\n".join(ocr_text)
    return full_markdown


