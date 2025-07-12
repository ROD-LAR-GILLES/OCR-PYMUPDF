"""
Módulo principal del proyecto OCR-PYMUPDF.

Este archivo inicia la interfaz de línea de comandos para seleccionar y procesar archivos PDF.
"""

from interfaces.cli_menu import mostrar_menu

def main() -> None:
    """Ejecuta el menú principal de la aplicación."""
    mostrar_menu()

if __name__ == "__main__":
    main()
    
