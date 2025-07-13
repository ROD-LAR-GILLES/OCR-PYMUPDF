"""
Módulo principal del sistema OCR-PYMUPDF.

Este archivo actúa como punto de entrada de la aplicación. Inicializa el sistema de logging y lanza la interfaz de
línea de comandos (CLI) para que el usuario pueda seleccionar archivos PDF, procesarlos, y generar versiones en Markdown.

Forma parte de la capa de interfaz del sistema, y está diseñado para ejecutarse como script principal.
"""

from loguru import logger
from interfaces.cli_menu import mostrar_menu

def main() -> None:
    """
    Inicializa el registro de logs y ejecuta la interfaz principal de la aplicación.

    Si ocurre una excepción durante la ejecución, se captura y se registra en un archivo de log.
    """
    logger.add("ocr-pymupdf.log", rotation="1 MB")
    try:
        mostrar_menu()
    except Exception as exc:
        logger.exception(exc)
        print("[ERROR] Ocurrió un problema. Revisa ocr-pymupdf.log")


if __name__ == "__main__":
    main() 
