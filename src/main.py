from loguru import logger
import sys

# Importar el menú CLI
def importar_menu():
    from adapters.in.cli.cli_menu import mostrar_menu
    return mostrar_menu

def main() -> None:
    """Punto de entrada de la aplicacion OCR-PYMUPDF."""
    # Configuracion logging 
    logger.remove()
    
    # Procesar argumentos de linea de comando
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    log_level = "DEBUG" if "--log-level=DEBUG" in sys.argv else "INFO"
    
    # Anadir handler para consola
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Anadir handler para archivo
    logger.add(
        "ocr.json",
        serialize=True,
        rotation="10 MB",
        level=log_level
    )
    
    logger.debug(f"Log level set to: {log_level}")
    
    # Modo no interactivo
    if args:
        from pathlib import Path
        from application.use_cases.pdf_to_markdown import PDFToMarkdownUseCase
        from adapters.out.ocr.pymupdf_adapter import PyMuPDFAdapter
        from adapters.out.storage.file_storage import FileStorage

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
                llm_port=None  # Modo sin LLM para la linea de comandos
            )
            md_path = use_case.execute(pdf_arg)
            print(f"[OK] Markdown generado: {md_path}")
        except Exception as exc:
            logger.exception(exc)
            print("[ERROR] Fallo la conversion a Markdown.")
        return  # Salir sin mostrar menu
        
    try:
        # Importar el menú de forma dinámica para evitar problemas de importación circular
        mostrar_menu = importar_menu()
        mostrar_menu()
    except Exception as exc:
        logger.exception(exc)
        print("[ERROR] Ocurrio un problema. Revisa ocr.json")


if __name__ == "__main__":
    main()
