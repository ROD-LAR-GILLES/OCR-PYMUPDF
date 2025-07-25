#!/usr/bin/env python
"""
Script para iniciar la interfaz web de OCR-PYMUPDF
"""
import os
import sys
from pathlib import Path

# Añadir el directorio src al path para importar módulos
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from src.interfaces.web.api.app import start_app

if __name__ == "__main__":
    # Iniciar la aplicación web
    start_app()