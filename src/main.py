from loguru import logger
from interfaces.cli_menu import mostrar_menu
import sys

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
    
    # Procesar argumentos de línea de comando
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    log_level = "DEBUG" if "--log-level=DEBUG" in sys.argv else "INFO"
    
    # Añadir handler para consola
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Añadir handler para archivo
    logger.add(
        "ocr.json",
        serialize=True,
        rotation="10 MB",
        level=log_level
    )
    
    logger.debug(f"Log level set to: {log_level}")
    
    # ─── Modo no interactivo ───
    if args:
        from pathlib import Path
        from domain.use_cases import PDFToMarkdownUseCase
        from adapters.pymupdf_adapter import PyMuPDFAdapter
        from infrastructure.file_storage import FileStorage

        pdf_arg = Path(args[0])
        if not pdf_arg.exists():
            print(f"[ERROR] El archivo {pdf_arg} no existe")
            return

        try:
            # Inicializar los puertos necesarios
            document_port = PyMuPDFAdapter()
            storage_port = FileStorage()
            
            # Crear y ejecutar el caso de uso
            use_case = PDFToMarkdownUseCase(
                document_port=document_port,
                storage_port=storage_port,
                llm_port=None  # Modo sin LLM para la línea de comandos
            )
            md_path = use_case.execute(pdf_arg)
            print(f"[OK] Markdown generado: {md_path}")
        except Exception as exc:
            logger.exception(exc)
            print("[ERROR] Falló la conversión a Markdown.")
        return  # Salir sin mostrar menú
        
    try:
        mostrar_menu()
    except Exception as exc:
        logger.exception(exc)
        print("[ERROR] Ocurrió un problema. Revisa ocr.json")


if __name__ == "__main__":
    main()
