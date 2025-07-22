#!/usr/bin/env python
# -*- coding: utf-8 -*-

from loguru import logger
import sys

def main():
    print("Iniciando aplicación OCR-PYMUPDF")
    logger.info("Aplicación iniciada")
    
    try:
        # Importamos aquí para evitar problemas de importación circular
        import adapters.inbound.cli.cli_menu as cli
        cli.mostrar_menu()
    except Exception as e:
        print(f"Error: {e}")
        logger.exception("Error al iniciar la aplicación")

if __name__ == "__main__":
    main()