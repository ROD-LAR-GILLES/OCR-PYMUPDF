#!/usr/bin/env python
"""
Script para iniciar la API REST de OCR-PYMUPDF
"""
import os
import sys
from pathlib import Path

# Añadir el directorio src al path para importar módulos
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from infrastructure.http.api_server import start_server

if __name__ == "__main__":
    # Obtener host y puerto de las variables de entorno o usar valores por defecto
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    # Iniciar el servidor
    start_server(host=host, port=port)