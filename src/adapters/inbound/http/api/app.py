"""Aplicación principal para la API web de OCR-PYMUPDF.

Este módulo configura la aplicación FastAPI para la interfaz web,
incluye las rutas y middleware necesarios.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

# Crear aplicación FastAPI
app = FastAPI(
    title="OCR-PYMUPDF Web",
    description="Interfaz web para OCR-PYMUPDF",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, limitar a orígenes específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta para verificar que la API está funcionando
@app.get("/api/health")
async def health_check():
    """Endpoint para verificar que la API está funcionando."""
    return {"status": "ok"}

# Configurar archivos estáticos para el frontend
frontend_dir = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

# Función para iniciar la aplicación
def start_app():
    """Inicia la aplicación FastAPI."""
    import uvicorn
    
    # Configurar host y puerto
    host = os.getenv("WEB_HOST", "0.0.0.0")
    port = int(os.getenv("WEB_PORT", "8080"))
    
    # Iniciar el servidor
    uvicorn.run(
        "adapters.inbound.http.api.app:app",
        host=host,
        port=port,
        reload=True,  # Habilitar recarga automática en desarrollo
        log_level="info"
    )

if __name__ == "__main__":
    start_app()