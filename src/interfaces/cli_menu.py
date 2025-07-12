"""Menú interactivo para seleccionar y procesar PDFs."""
from pathlib import Path
import questionary
from domain.use_cases import convert_pdf_to_md
from loguru import logger

PDF_DIR = Path("pdfs")


def mostrar_menu() -> None:
    """Lista PDF en ./pdfs y procesa el seleccionado."""
    archivos = sorted(PDF_DIR.glob("*.pdf"))
    if not archivos:
        print("[INFO] No se encontraron PDF en ./pdfs. Copia alguno y vuelve a ejecutar.")
        return

    seleccion = questionary.select(
        "Selecciona un PDF para convertir a Markdown:",
        choices=[a.name for a in archivos],
    ).ask()

    if not seleccion:
        return

    pdf_path = PDF_DIR / seleccion
    logger.info(f"Procesando {pdf_path}")
    md_path = convert_pdf_to_md(pdf_path)
    print(f"[OK] Markdown generado: {md_path}")