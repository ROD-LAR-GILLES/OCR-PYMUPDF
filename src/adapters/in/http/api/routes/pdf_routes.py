"""Rutas para la gestión de documentos PDF en la interfaz web.

Este módulo define las rutas específicas para la gestión de documentos
PDF en la interfaz web, incluyendo subida, procesamiento y descarga.
"""
from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional
import os
import shutil
from pathlib import Path

# Importaciones del dominio
from domain.use_cases.pdf_to_markdown import PDFToMarkdownUseCase
from domain.dtos.document_dtos import DocumentInputDTO

# Importaciones de adaptadores
from adapters.pymupdf_adapter import PyMuPDFAdapter
from adapters.llm_refiner import LLMRefiner

# Importaciones de infraestructura
from infrastructure.file_storage import FileStorage
from infrastructure.http.document_service import DocumentService
from infrastructure.http.models import (
    DocumentCreate, 
    DocumentResponse, 
    DocumentStatus,
    DocumentDetail,
    ErrorResponse
)

# Crear router
router = APIRouter(prefix="/api/documents", tags=["documents"])

# Directorios para almacenar archivos
UPLOAD_DIR = Path("uploads")
RESULT_DIR = Path("resultado")

# Crear directorios necesarios
UPLOAD_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)

# Dependencias para inyección
def get_pdf_to_markdown_use_case(use_llm: bool = False):
    """Proporciona una instancia configurada del caso de uso PDFToMarkdownUseCase."""
    document_port = PyMuPDFAdapter()
    storage_port = FileStorage()
    llm_port = LLMRefiner() if use_llm else None
    return PDFToMarkdownUseCase(document_port, storage_port, llm_port)

# Función para procesar documentos en segundo plano
async def process_document(input_dto: DocumentInputDTO, doc_id: str, use_case: PDFToMarkdownUseCase):
    """Procesa un documento PDF en segundo plano.
    
    Args:
        input_dto: DTO con la información del documento a procesar
        doc_id: ID único del documento
        use_case: Caso de uso para procesar el documento
    """
    try:
        # Actualizar estado a "processing"
        DocumentService.update_document_status(doc_id, "processing", 0.0)
        
        # Registrar tiempo de inicio
        start_time = time.time()
        
        # Procesar documento
        result = use_case.execute(input_dto)
        
        # Calcular tiempo de procesamiento
        processing_time = time.time() - start_time
        
        # Actualizar estado a "completed"
        DocumentService.update_document_status(
            doc_id, 
            "completed", 
            100.0, 
            metadata={
                "total_pages": result.total_pages,
                "processing_time": processing_time,
                "language": result.language
            }
        )
    except Exception as e:
        # Actualizar estado a "error"
        DocumentService.update_document_status(
            doc_id, 
            "error", 
            0.0, 
            error_message=str(e)
        )
        raise

@router.get("/", response_model=List[DocumentStatus])
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

@router.post("/", response_model=DocumentResponse, responses={400: {"model": ErrorResponse}})
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

@router.get("/{doc_id}/status", response_model=DocumentStatus, responses={404: {"model": ErrorResponse}})
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
        
        # Devolver estado
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
        raise HTTPException(
            status_code=404,
            detail=f"Documento con ID {doc_id} no encontrado"
        )

@router.get("/{doc_id}/download", responses={404: {"model": ErrorResponse}})
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

@router.delete("/{doc_id}", responses={404: {"model": ErrorResponse}})
async def delete_document(doc_id: str):
    """Elimina un documento y sus archivos asociados.
    
    Args:
        doc_id: ID único del documento
        
    Returns:
        dict: Mensaje de confirmación
    """
    try:
        # Obtener metadatos del documento
        metadata = DocumentService.get_document(doc_id)
        
        # Eliminar archivo PDF
        for file in UPLOAD_DIR.glob(f"{doc_id}*"):
            os.remove(file)
        
        # Eliminar archivo Markdown
        for file in RESULT_DIR.glob(f"*{doc_id}*.md"):
            os.remove(file)
        
        # Eliminar metadatos
        DocumentService.delete_document(doc_id)
        
        return {"message": "Documento eliminado correctamente"}
    except FileNotFoundError:
        return JSONResponse(
            status_code=404,
            content={"detail": f"Documento con ID {doc_id} no encontrado"}
        )