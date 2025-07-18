from loguru import logger
from interfaces.cli_menu import mostrar_menu

def main() -> None:
    """
    Punto de entrada de la aplicación OCR-PYMUPDF.
    
    Configura el sistema de logging para:
    - Eliminar el handler por defecto de Loguru
    - Añadir handler para escribir en ocr.json en formato JSON
    - Rotar archivo cada 10 MB
    
    Invoca el menú interactivo CLI.
    """
    # Configuración logging 
    logger.remove()
    logger.add(
        "ocr.json",
        serialize=True,
        rotation="10 MB"
    )
    
    try:
        mostrar_menu()
    except Exception as exc:
        logger.exception(exc)
        print("[ERROR] Ocurrió un problema. Revisa ocr.json")


if __name__ == "__main__":
    main()
