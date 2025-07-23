#!/usr/bin/env python
"""
Script para iniciar la API REST de OCR-PYMUPDF
"""
import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path para importar módulos
root_path = Path(__file__).parents[2]
sys.path.insert(0, str(root_path))

import uvicorn

if __name__ == "__main__":
    # Obtener host y puerto de las variables de entorno o usar valores por defecto
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    # Iniciar el servidor
    uvicorn.run(
        "adapters.inbound.http.api.app:app",
        host=host,
        port=port,
        reload=True
    )