"""
Caso de uso para convertir archivos PDF a formato Markdown utilizando PyMuPDF4LLM y OCR si es necesario.

Este módulo forma parte de la capa de dominio y contiene lógica de negocio independiente de infraestructura.
Se encarga de coordinar la extracción de contenido (a través del adaptador) y el guardado (a través de la infraestructura).
"""
from pathlib import Path
from adapters.pymupdf_adapter import extract_markdown
from infrastructure.file_storage import save_markdown
from utils.detect_errores import revisar_documento
from utils.train_fasttext import train 

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
    return save_markdown(pdf_path.stem, markdown)

def convert_pdf_to_md(pdf_path: Path) -> Path:
    markdown = extract_markdown(pdf_path)
    md_path = save_markdown(pdf_path.stem, markdown)

    # ── Pos-OCR: revisión interactiva ──
    revisar_documento(markdown.split())   
    train()                              

    return md_path