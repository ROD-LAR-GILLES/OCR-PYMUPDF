"""Script para iniciar el servidor API de OCR-PYMUPDF.

Este script configura y ejecuta el servidor API utilizando Uvicorn.
"""
import uvicorn
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear directorios necesarios
Path("uploads").mkdir(exist_ok=True)
Path("resultado").mkdir(exist_ok=True)

def main():
    """Función principal para iniciar el servidor API."""
    # Configurar host y puerto
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    # Iniciar el servidor
    uvicorn.run(
        "infrastructure.http.api:app",
        host=host,
        port=port,
        reload=True,  # Habilitar recarga automática en desarrollo
        log_level="info"
    )

if __name__ == "__main__":
    main()