"""
Rutas para diagnóstico de problemas en la API.

Este módulo define rutas que permiten realizar diagnósticos de problemas
con el procesamiento de documentos y el estado del sistema.
"""
from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import os
import sys
import platform
import time
from datetime import datetime
from pathlib import Path as PathLib

from infrastructure.diagnostics import diagnose_pdf_processing, test_ocr_capability
from infrastructure.logging_setup import logger

# Crear router
router = APIRouter(prefix="/api/diagnostics", tags=["diagnostics"])

@router.get("/system")
async def get_system_info() -> Dict[str, Any]:
    """
    Obtiene información sobre el sistema, útil para diagnóstico.
    
    Returns:
        Dict[str, Any]: Información del sistema
    """
    try:
        # Información básica del sistema
        system_info = {
            "timestamp": datetime.now().isoformat(),
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": sys.version,
                "python_implementation": platform.python_implementation()
            },
            "process": {
                "pid": os.getpid(),
                "cwd": os.getcwd(),
                "uptime": time.time() - process_start_time
            },
            "environment": {
                "env_vars": {k: v for k, v in os.environ.items() if not k.lower().startswith(('pass', 'secret', 'key', 'token'))}
            }
        }
        
        # Información sobre bibliotecas y dependencias
        try:
            import pkg_resources
            installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
            system_info["dependencies"] = installed_packages
        except Exception as e:
            system_info["dependencies_error"] = str(e)
        
        # Información sobre espacio en disco
        try:
            import shutil
            disk_usage = shutil.disk_usage("/")
            system_info["disk"] = {
                "total_gb": disk_usage.total / (1024**3),
                "used_gb": disk_usage.used / (1024**3),
                "free_gb": disk_usage.free / (1024**3),
                "percent_used": disk_usage.used / disk_usage.total * 100
            }
        except Exception as e:
            system_info["disk_error"] = str(e)
        
        # Información sobre memoria
        try:
            import psutil
            memory = psutil.virtual_memory()
            system_info["memory"] = {
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "used_gb": memory.used / (1024**3),
                "percent_used": memory.percent
            }
        except Exception as e:
            system_info["memory_error"] = str(e)
        
        return system_info
    
    except Exception as e:
        logger.error(f"Error al obtener información del sistema: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener información del sistema: {str(e)}")

@router.get("/ocr")
async def test_ocr(text: str = Query("Este es un texto de prueba para OCR")) -> Dict[str, Any]:
    """
    Prueba las capacidades de OCR del sistema.
    
    Args:
        text: Texto de prueba para OCR
        
    Returns:
        Dict[str, Any]: Resultados de la prueba de OCR
    """
    try:
        result = test_ocr_capability(text)
        return result
    except Exception as e:
        logger.error(f"Error al probar OCR: {e}")
        raise HTTPException(status_code=500, detail=f"Error al probar OCR: {str(e)}")

@router.get("/document/{doc_id}")
async def diagnose_document(doc_id: str = Path(..., description="ID del documento a diagnosticar")) -> Dict[str, Any]:
    """
    Diagnostica problemas con un documento específico.
    
    Args:
        doc_id: ID del documento
        
    Returns:
        Dict[str, Any]: Resultados del diagnóstico
    """
    try:
        # Intentar encontrar el documento en diferentes ubicaciones
        uploads_dir = PathLib("uploads")
        result_dir = PathLib("resultado")
        
        # Buscar en directorio de uploads
        document_path = None
        if uploads_dir.exists():
            for file in uploads_dir.glob(f"{doc_id}*"):
                document_path = file
                break
        
        # Si no se encuentra, buscar en directorio de resultados
        if document_path is None and result_dir.exists():
            for file in result_dir.glob(f"{doc_id}*"):
                document_path = file
                break
        
        if document_path is None:
            raise HTTPException(status_code=404, detail=f"Documento con ID {doc_id} no encontrado")
        
        # Diagnosticar el documento
        result = diagnose_pdf_processing(document_path)
        
        # Añadir información del documento
        result["document_info"] = {
            "id": doc_id,
            "path": str(document_path),
            "filename": document_path.name
        }
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al diagnosticar documento {doc_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al diagnosticar documento: {str(e)}")

# Tiempo de inicio del proceso
process_start_time = time.time()
