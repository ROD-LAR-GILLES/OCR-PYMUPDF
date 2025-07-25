#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import traceback
from pathlib import Path

# Configurar filtros de advertencias temprano
try:
    from infrastructure.warnings_config import configure_warnings
    configure_warnings()
except ImportError:
    pass  # Silenciosamente continuar si no podemos importar

# Importar logger después de configurar advertencias
from loguru import logger

# Configurar directorio de logs
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Importar el menú CLI
def importar_menu():
    try:
        from adapters.inbound.cli.cli_menu import mostrar_menu
        return mostrar_menu
    except ImportError as e:
        logger.error(f"Error al importar el menú CLI: {e}")
        print(f"[ERROR] No se pudo cargar el menú CLI: {e}")
        sys.exit(1)

def configurar_logging():
    """Configuración del sistema de logging"""
    # Eliminar handlers por defecto
    logger.remove()
    
    # Procesar argumentos para nivel de log
    log_level = "DEBUG" if "--log-level=DEBUG" in sys.argv else "INFO"
    
    # Añadir handler para consola
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Añadir handler para archivo de log general
    logger.add(
        "logs/ocr_app.log",
        rotation="10 MB",
        retention="1 week",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    # Añadir handler para errores
    logger.add(
        "logs/ocr_errors.log",
        rotation="5 MB",
        retention="1 month",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    # Añadir handler para logs JSON
    logger.add(
        "logs/ocr.json",
        serialize=True,
        rotation="10 MB",
        level=log_level
    )
    
    logger.debug(f"Log level set to: {log_level}")
    logger.info(f"Sistema de logs inicializado en directorio: {logs_dir.absolute()}")

def procesar_pdf_no_interactivo(pdf_arg):
    """Procesa un PDF en modo no interactivo"""
    from pathlib import Path
    from application.use_cases.pdf_to_markdown import PDFToMarkdownUseCase
    
    # Importar adaptadores solo cuando se necesitan
    try:
        from adapters.out.ocr.pymupdf_adapter import PyMuPDFAdapter
        from adapters.out.storage.file_storage import FileStorage
    except ImportError as e:
        logger.error(f"Error al importar adaptadores: {e}")
        print(f"[ERROR] No se pudieron cargar los adaptadores necesarios: {e}")
        return

    pdf_path = Path(pdf_arg)
    if not pdf_path.exists():
        logger.error(f"El archivo {pdf_path} no existe")
        print(f"[ERROR] El archivo {pdf_path} no existe")
        return

    logger.info(f"Procesando archivo: {pdf_path}")
    try:
        # Verificar el tamaño del archivo
        file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
        logger.info(f"Tamaño del archivo: {file_size_mb:.2f} MB")
        
        # Verificar permisos
        logger.info(f"Permisos de archivo: {oct(os.stat(pdf_path).st_mode)[-3:]}")
        
        # Inicializar los puertos necesarios
        document_port = PyMuPDFAdapter()
        storage_port = FileStorage()
        
        # Crear y ejecutar el caso de uso
        use_case = PDFToMarkdownUseCase(
            document_port=document_port,
            storage_port=storage_port,
            llm_port=None  # Modo sin LLM para la linea de comandos
        )
        
        logger.info("Iniciando conversión de PDF a Markdown")
        md_path = use_case.execute(pdf_path)
        logger.info(f"Conversión completada: {md_path}")
        print(f"[OK] Markdown generado: {md_path}")
    except Exception as exc:
        logger.exception("Error durante la conversión")
        # Detallar el error
        exc_type, exc_value, exc_tb = sys.exc_info()
        tb_list = traceback.format_exception(exc_type, exc_value, exc_tb)
        for line in tb_list:
            logger.error(line.strip())
        
        print(f"[ERROR] Fallo la conversión a Markdown: {exc}")
        print(f"Consulte los logs en {logs_dir.absolute()} para más detalles")

def main() -> None:
    """Punto de entrada de la aplicacion OCR-PYMUPDF."""
    # Configurar sistema de logs
    configurar_logging()
    
    logger.info("=== Iniciando aplicación OCR-PYMUPDF ===")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Sistema operativo: {sys.platform}")
    
    # Procesar argumentos de linea de comando
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    
    # Modo no interactivo
    if args:
        logger.info(f"Modo no interactivo con argumentos: {args}")
        procesar_pdf_no_interactivo(args[0])
        return  # Salir sin mostrar menu
        
    # Modo interactivo
    try:
        logger.info("Iniciando modo interactivo")
        # Importar el menú de forma dinámica para evitar problemas de importación circular
        mostrar_menu = importar_menu()
        mostrar_menu()
    except KeyboardInterrupt:
        logger.info("Aplicación terminada por el usuario (Ctrl+C)")
        print("\nAplicación terminada.")
    except Exception as exc:
        logger.exception("Error en modo interactivo")
        print(f"[ERROR] Ocurrió un problema. Revisa logs/ocr_errors.log")
    finally:
        logger.info("=== Finalizando aplicación OCR-PYMUPDF ===")


if __name__ == "__main__":
    main()
