"""Módulo principal de la API REST para OCR-PYMUPDF.

Este módulo implementa una API REST utilizando FastAPI para proporcionar
acceso a las funcionalidades de OCR y procesamiento de PDF del sistema.
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil
import os
import time
from typing import List, Optional, Dict, Any

# Importaciones del dominio
from application.use_cases.pdf_to_markdown import PDFToMarkdownUseCase
from domain.dtos.document_dtos import DocumentInputDTO

# Importaciones de adaptadores
from adapters.out.ocr.pymupdf_adapter import PyMuPDFAdapter
from adapters.out.llm.llm_refiner import LLMRefiner

# Importaciones de infraestructura
from adapters.out.storage.file_storage import FileStorage
from adapters.inbound.http.document_service import DocumentService
from adapters.inbound.http.models import (
    DocumentCreate, 
    DocumentResponse, 
    DocumentStatus,
    DocumentDetail,
    ErrorResponse
)

# Importar router de usuarios
from adapters.inbound.http.api.routes.user_routes import router as user_router

# Directorios para almacenar archivos
UPLOAD_DIR = Path("uploads")
RESULT_DIR = Path("resultado")
METADATA_DIR = Path("metadata")

# Crear directorios necesarios
UPLOAD_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)
METADATA_DIR.mkdir(exist_ok=True)

# Crear la aplicación FastAPI
app = FastAPI(
    title="OCR-PYMUPDF API",
    description="API para procesamiento de documentos PDF con OCR y extracción de texto",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, limitar a orígenes específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir router de usuarios
app.include_router(user_router)

# Dependencias para inyección
def get_pdf_to_markdown_use_case(use_llm: bool = False):
    """Proporciona una instancia configurada del caso de uso PDFToMarkdownUseCase."""
    document_port = PyMuPDFAdapter()
    storage_port = FileStorage()
    llm_port = LLMRefiner() if use_llm else None
    return PDFToMarkdownUseCase(document_port, storage_port, llm_port)

@app.get("/api/")
async def root():
    """Endpoint raíz para verificar que la API está funcionando."""
    return {"message": "OCR-PYMUPDF API está funcionando"}

@app.get("/api/health")
async def health_check():
    """Endpoint para verificar el estado de salud de la API."""
    return {"status": "ok"}


@app.get("/api/documents/", response_model=List[DocumentStatus])
async def list_documents(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Lista los documentos disponibles.
    
    Args:
        limit: Número máximo de documentos a devolver
        offset: Número de documentos a saltar
        
    Returns:
        List[DocumentStatus]: Lista de estados de documentos
    """
    # Obtener lista de documentos
    documents = DocumentService.list_documents(limit, offset)
    
    # Convertir a modelo de respuesta
    result = []
    for doc in documents:
        # Convertir fechas de texto a objetos datetime
        from datetime import datetime
        created_at = datetime.fromisoformat(doc["created_at"])
        updated_at = datetime.fromisoformat(doc["updated_at"]) if doc["updated_at"] else None
        
        # Añadir a la lista de resultados
        result.append(DocumentStatus(
            id=doc["id"],
            filename=doc["filename"],
            status=doc["status"],
            progress=doc["progress"],
            created_at=created_at,
            updated_at=updated_at,
            error_message=doc["error_message"]
        ))
    
    return result

@app.post("/api/documents/", response_model=DocumentResponse, responses={400: {"model": ErrorResponse}})
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    options: DocumentCreate = Depends()
):
    """Sube un archivo PDF para procesamiento.
    
    Args:
        file: Archivo PDF a procesar
        options: Opciones de procesamiento
        
    Returns:
        DocumentResponse: Información sobre el documento procesado
    """
    # Validar que sea un PDF
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(
            status_code=400,
            content={"detail": "El archivo debe ser un PDF"}
        )
    
    try:
        # Crear documento en el servicio
        doc_id = DocumentService.create_document(
            filename=file.filename,
            options=options.dict()
        )
        
        # Definir ruta del archivo
        file_path = UPLOAD_DIR / f"{doc_id}_{file.filename}"
        
        # Guardar el archivo subido
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Actualizar estado a "processing"
        DocumentService.update_document_status(doc_id, "processing", 0.0)
        
        # Crear DTO de entrada
        input_dto = DocumentInputDTO(
            file_path=str(file_path),
            process_tables=options.process_tables,
            detect_language=options.detect_language,
            spell_check=options.spell_check,
            refine_with_llm=options.use_llm
        )
        
        # Obtener caso de uso apropiado
        use_case = get_pdf_to_markdown_use_case(options.use_llm)
        
        # Procesar el documento en segundo plano
        background_tasks.add_task(
            process_document,
            input_dto=input_dto,
            doc_id=doc_id,
            use_case=use_case
        )
        
        # Construir URL para descargar el resultado
        base_url = f"/api/documents/{doc_id}/download"
        
        # Devolver respuesta inmediata
        return DocumentResponse(
            id=doc_id,
            filename=file.filename,
            total_pages=0,  # Se actualizará después del procesamiento
            processed_successfully=True,
            processing_time=None,
            markdown_url=base_url,
            created_at=DocumentService.get_document(doc_id)["created_at"]
        )
    except Exception as e:
        # Eliminar el archivo en caso de error
        if 'file_path' in locals() and Path(file_path).exists():
            os.remove(file_path)
        
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error al procesar el documento: {str(e)}"}
        )

async def process_document(input_dto: DocumentInputDTO, doc_id: str, use_case: PDFToMarkdownUseCase):
    """Procesa un documento en segundo plano.
    
    Args:
        input_dto: DTO con la información del documento
        doc_id: ID único del documento
        use_case: Caso de uso para procesar el documento
    """
    start_time = time.time()
    
    try:
        # Actualizar progreso
        DocumentService.update_document_status(doc_id, "processing", 10.0)
        
        # Ejecutar el caso de uso
        result_path = use_case.execute(Path(input_dto.file_path))
        
        # Calcular tiempo de procesamiento
        processing_time = time.time() - start_time
        
        # Actualizar estado a "completed"
        DocumentService.update_document_status(doc_id, "completed", 100.0)
        
        # Actualizar metadatos con información adicional
        metadata = DocumentService.get_document(doc_id)
        metadata["processing_time"] = processing_time
        metadata["result_path"] = str(result_path)
        
        # Guardar metadatos actualizados
        with open(METADATA_DIR / f"{doc_id}.json", "w") as f:
            import json
            json.dump(metadata, f, indent=2)
            
    except Exception as e:
        # Registrar el error
        from infrastructure.logging_setup import logger
        logger.error(f"Error al procesar el documento {doc_id}: {str(e)}")
        
        # Actualizar estado a "error"
        DocumentService.update_document_status(doc_id, "error", error_message=str(e))

@app.get("/api/documents/{doc_id}/status", response_model=DocumentStatus, responses={404: {"model": ErrorResponse}})
async def get_document_status(doc_id: str):
    """Obtiene el estado de procesamiento de un documento.
    
    Args:
        doc_id: ID único del documento
        
    Returns:
        DocumentStatus: Estado del documento
    """
    try:
        # Obtener metadatos del documento
        metadata = DocumentService.get_document(doc_id)
        
        # Convertir fechas de texto a objetos datetime
        from datetime import datetime
        created_at = datetime.fromisoformat(metadata["created_at"])
        updated_at = datetime.fromisoformat(metadata["updated_at"]) if metadata["updated_at"] else None
        
        # Construir respuesta
        return DocumentStatus(
            id=metadata["id"],
            filename=metadata["filename"],
            status=metadata["status"],
            progress=metadata["progress"],
            created_at=created_at,
            updated_at=updated_at,
            error_message=metadata["error_message"]
        )
    except FileNotFoundError:
        return JSONResponse(
            status_code=404,
            content={"detail": f"Documento con ID {doc_id} no encontrado"}
        )

@app.get("/api/documents/{doc_id}/download", responses={404: {"model": ErrorResponse}})
async def download_document(doc_id: str):
    """Descarga el documento procesado.
    
    Args:
        doc_id: ID único del documento
        
    Returns:
        FileResponse: Archivo Markdown procesado
    """
    try:
        # Obtener metadatos del documento
        metadata = DocumentService.get_document(doc_id)
        
        # Verificar si el documento está procesado
        if metadata["status"] != "completed":
            return JSONResponse(
                status_code=404,
                content={"detail": "El documento aún no ha sido procesado completamente"}
            )
        
        # Buscar el archivo Markdown correspondiente
        for file in RESULT_DIR.glob(f"*{doc_id}*.md"):
            return FileResponse(
                path=file,
                media_type="text/markdown",
                filename=f"{metadata['filename'].replace('.pdf', '.md')}"
            )
        
        # Si no se encuentra el archivo pero el estado es "completed"
        return JSONResponse(
            status_code=404,
            content={"detail": "Archivo de resultado no encontrado"}
        )
    except FileNotFoundError:
        return JSONResponse(
            status_code=404,
            content={"detail": f"Documento con ID {doc_id} no encontrado"}
        )

@app.delete("/api/documents/{doc_id}", responses={404: {"model": ErrorResponse}})
async def delete_document(doc_id: str):
    """Elimina un documento y sus resultados.
    
    Args:
        doc_id: ID único del documento
        
    Returns:
        dict: Confirmación de eliminación
    """
    # Usar el servicio para eliminar el documento
    deleted = DocumentService.delete_document(doc_id)
    
    if not deleted:
        return JSONResponse(
            status_code=404,
            content={"detail": f"Documento con ID {doc_id} no encontrado"}
        )
    
    return {"message": "Documento eliminado correctamente"}