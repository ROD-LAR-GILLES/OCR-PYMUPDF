"""
Adaptador para extracción de contenido de archivos PDF a formato Markdown, utilizando PyMuPDF4LLM para PDFs digitales
y OCR (Tesseract) como mecanismo de respaldo en caso de PDFs escaneados (sin texto seleccionable).

Este módulo cumple la función de adaptador dentro de la arquitectura limpia, delegando la lógica de extracción de texto
a herramientas externas y encapsulando la decisión sobre el método adecuado de procesamiento.
"""
from pathlib import Path
import fitz
from loguru import logger
from adapters.ocr_adapter import perform_ocr_on_page, needs_ocr
import camelot
import pdfplumber
from tabulate import tabulate

def extract_tables_markdown(pdf_path: Path) -> str:
    """
    Extrae tablas del PDF y las devuelve en formato Markdown.

    Prioridad:
        1. Camelot (tablas con bordes).
        2. pdfplumber (respaldo para tablas sin bordes).

    Args:
        pdf_path (Path): Ruta al PDF.

    Returns:
        str: Markdown con todas las tablas o cadena vacía.
    """
    md_parts: list[str] = []

    # Intento con Camelot
    try:
        tables = camelot.read_pdf(str(pdf_path), pages="all")
        if tables:
            md_parts.append("## Tablas Detectadas (Camelot)\n")
            for i, tabla in enumerate(tables, 1):
                md_parts.append(f"### Tabla {i}\n\n")
                md_parts.append(tabla.df.to_markdown())
                md_parts.append("\n")
    except Exception as exc:
        logger.warning(f"Error con Camelot: {exc}")

    # Respaldo con pdfplumber
    if not md_parts:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, pg in enumerate(pdf.pages, 1):
                    tablas = pg.extract_tables()
                    if tablas:
                        md_parts.append(f"## Tablas Detectadas (Página {i})\n")
                        for j, t in enumerate(tablas, 1):
                            md_parts.append(f"### Tabla {j}\n\n")
                            md_parts.append(tabulate(t, tablefmt="pipe"))
                            md_parts.append("\n")
        except Exception as exc:
            logger.warning(f"Error con pdfplumber: {exc}")

    return "\n".join(md_parts)

def extract_markdown(pdf_path: Path) -> str:
    """
    Extrae el contenido de un archivo PDF en formato Markdown. Usa OCR si se detecta que una página no contiene texto.

    Args:
        pdf_path (Path): Ruta al archivo PDF.

    Returns:
        str: Contenido en formato Markdown.
    """
    logger.info("Iniciando análisis de páginas individuales para aplicar OCR selectivo si es necesario.")

    with fitz.open(pdf_path) as doc:
        ocr_text: list[str] = []
        for i, page in enumerate(doc):
            if needs_ocr(page):
                logger.info(f"[Página {i + 1}] Sin texto detectable. Aplicando OCR...")
                text = perform_ocr_on_page(page)
            else:
                logger.info(f"[Página {i + 1}] Texto detectado. Extrayendo directamente...")
                text = page.get_text("text")
            ocr_text.append(f"## Página {i + 1}\n\n{text.strip()}")

    full_markdown = f"# {pdf_path.stem}\n\n" + "\n\n".join(ocr_text)

    # Anexar tablas si existen
    tables_md = extract_tables_markdown(pdf_path)
    if tables_md:
        full_markdown += "\n\n" + tables_md

    return full_markdown


