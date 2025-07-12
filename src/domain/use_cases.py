"""Casos de uso para conversión de PDF a Markdown."""
from pathlib import Path
from adapters.pymupdf_adapter import extract_markdown
from infrastructure.file_storage import save_markdown


def convert_pdf_to_md(pdf_path: Path) -> Path:
    """Convierte un PDF a Markdown y lo guarda.

    Args:
        pdf_path: Ruta al PDF de entrada.

    Returns:
        Ruta del Markdown generado.
    """
    markdown = extract_markdown(pdf_path)
    return save_markdown(pdf_path.stem, markdown)