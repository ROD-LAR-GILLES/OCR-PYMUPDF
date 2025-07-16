from loguru import logger
from interfaces.cli_menu import mostrar_menu

def main() -> None:
    """
    Punto de entrada de la aplicación OCR-PYMUPDF.

    Configura el sistema de logging para que:
    * Se elimine el handler por defecto de Loguru (que escribe en consola).
    * Se añada un handler que escribe en `ocr.json` en formato JSON
      (``serialize=True``) y rota el archivo cada 10 MB.

    Luego invoca el menú interactivo (CLI).  
    Si ocurre cualquier excepción no controlada, la registra con
    ``logger.exception`` y muestra un mensaje amigable en consola.

    Returns
    -------
    None
    """
    # ─── Logging estructurado ─────────────────────────────────────────────
    logger.remove()                                   # Elimina stdout default
    logger.add(
        "ocr.json",
        serialize=True,                               # JSON estructurado
        rotation="10 MB"                              # Rota al llegar a 10 MB
    )
    # Si deseas mantener la salida por consola, descomenta:
    # logger.add(sys.stderr, level="INFO")

    # ─── Lanzar CLI ──────────────────────────────────────────────────────
    try:
        mostrar_menu()
    except Exception as exc:
        logger.exception(exc)  # Traza completa al archivo JSON
        print("[ERROR] Ocurrió un problema. Revisa ocr.json")


if __name__ == "__main__":
    main() 
