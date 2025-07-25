"""Aplicación principal para la API web de OCR-PYMUPDF.

Este módulo configura la aplicación FastAPI para la interfaz web,
incluye las rutas y middleware necesarios.
"""
# Configurar filtros de advertencias antes de importar otras dependencias
from infrastructure.warnings_setup import configure_warnings
configure_warnings()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

# Importar routers
from adapters.inbound.http.api.routes.user_routes import router as user_router
from adapters.inbound.http.api.routes.pdf_routes import router as pdf_router

# Importar validación de claves LLM
from infrastructure.llm_keys_check import check_llm_keys, get_available_llm_providers

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
@app.get("/health")
async def health_check():
    """Endpoint para verificar que la API está funcionando."""
    return {"status": "ok"}

# Añadir la ruta /api/health directamente en la aplicación principal
@app.get("/api/health")
async def api_health_check():
    """Endpoint para verificar que la API está funcionando."""
    return {"status": "ok"}

# Incluir los routers directamente en la aplicación principal
# Los routers ya tienen sus prefijos configurados (/api/users y /api/documents)
app.include_router(user_router)
app.include_router(pdf_router)

# Configurar archivos estáticos para el frontend
# IMPORTANTE: Montamos los archivos estáticos después de definir todas las rutas de la API
# para evitar que interfieran con las rutas de la API
frontend_dir = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dir.exists():
    # Montar en una ruta específica para evitar conflictos con las rutas de la API
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")
    # Montar la raíz para servir index.html al final, después de todas las rutas de la API
    # NOTA: Este montaje debe ser el último para evitar que capture las peticiones destinadas a la API
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

# Eventos de inicio y cierre de la aplicación
@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación."""
    # Verificar claves de API para LLM
    available_providers = get_available_llm_providers()
    if available_providers:
        print(f"Proveedores LLM disponibles: {', '.join(available_providers)}")
    else:
        print("ADVERTENCIA: No se encontraron claves de API para los proveedores LLM")
        print("El sistema funcionará en modo OCR básico sin refinamiento LLM")

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