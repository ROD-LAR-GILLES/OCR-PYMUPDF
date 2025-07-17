"""
Caso de uso para convertir archivos PDF a formato Markdown utilizando PyMuPDF4LLM y OCR si es necesario.

Este módulo forma parte de la capa de dominio y contiene lógica de negocio independiente de infraestructura.
Se encarga de coordinar la extracción de contenido (a través del adaptador) y el guardado (a través de la infraestructura).
"""
from pathlib import Path
from adapters.pymupdf_adapter import extract_markdown
from infrastructure.file_storage import save_markdown

def convert_pdf_to_md(pdf_path: Path) -> Path:
    """
    Convierte un archivo PDF en un archivo Markdown, utilizando extracción inteligente (digital u OCR)
    y guarda el resultado en el sistema de archivos.

    Args:
        pdf_path (Path): Ruta al archivo PDF de entrada.

    Returns:
        Path: Ruta al archivo Markdown generado y almacenado.
    """
    markdown = extract_markdown(pdf_path)
    md_path = save_markdown(pdf_path.stem, markdown)
    return md_path

def convert_pdf_to_html(pdf_path: Path) -> Path:
    """
    Convierte un archivo PDF a HTML y guarda el resultado.

    Args:
        pdf_path (Path): Ruta al archivo PDF.

    Returns:
        Path: Ruta al archivo HTML generado.
    """
    markdown = extract_markdown(pdf_path)
    html = markdown.replace("\n", "<br>\n")  # Simple conversión, puedes mejorar usando markdown2
    html_path = Path("resultado") / f"{pdf_path.stem}.html"
    html_path.write_text(html, encoding="utf-8")
    return html_path