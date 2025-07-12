"""
Módulo principal del proyecto OCR-PYMUPDF.

Este archivo inicia la interfaz de línea de comandos para seleccionar y procesar archivos PDF.
"""

from loguru import logger
from interfaces.cli_menu import mostrar_menu

def main() -> None:
    """Punto de entrada principal."""
    logger.add("ocr-pymupdf.log", rotation="1 MB")
    try:
        mostrar_menu()
    except Exception as exc:
        logger.exception(exc)
        print("[ERROR] Ocurrió un problema. Revisa ocr-pymupdf.log")


if __name__ == "__main__":
    main()  
