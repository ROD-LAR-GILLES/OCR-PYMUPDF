"""Rutas para la gestión de documentos PDF en la interfaz web.

Este módulo define las rutas específicas para la gestión de documentos
PDF en la interfaz web, incluyendo subida, procesamiento y descarga.
"""
from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional
import os
import shutil
import time
from pathlib import Path

# Importaciones del dominio
from domain.use_cases.pdf_to_markdown import PDFToMarkdownUseCase
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
    llm_port = _resolve_llm_port() if use_llm else None
    return PDFToMarkdownUseCase(document_port, storage_port, llm_port)

def _resolve_llm_port():
    """
    Resuelve dinámicamente el puerto LLM a utilizar según las claves de API disponibles.
    
    Returns:
        LLMPort or None: Una instancia del puerto LLM si hay claves disponibles, None en caso contrario
    """
    import os
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Verificar claves de API disponibles
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    # Elegir el proveedor según disponibilidad (orden de prioridad)
    if openai_key:
        logger.info("Usando OpenAI como proveedor LLM")
        return LLMRefiner(provider="openai")
    elif gemini_key:
        logger.info("Usando Gemini como proveedor LLM")
        return LLMRefiner(provider="gemini")
    elif anthropic_key:
        logger.info("Usando Anthropic como proveedor LLM")
        return LLMRefiner(provider="anthropic")
    else:
        logger.warning("No se encontraron claves de API para proveedores LLM. Desactivando refinamiento LLM.")
        return None

# Función para procesar documentos en segundo plano
async def process_document(input_dto: DocumentInputDTO, doc_id: str, use_case: PDFToMarkdownUseCase):
    """Procesa un documento PDF en segundo plano.
    
    Args:
        input_dto: DTO con la información del documento a procesar
        doc_id: ID único del documento
        use_case: Caso de uso para procesar el documento
    """
    from infrastructure.logging_setup import logger, log_error_details, log_document_processing
    
    try:
        # Registrar inicio del procesamiento
        logger.info(f"Iniciando procesamiento del documento {doc_id}: {input_dto.file_path}")
        
        # Actualizar estado a "processing"
        DocumentService.update_document_status(doc_id, "processing", 0.0)
        
        # Registrar en el log de documentos
        log_document_processing(
            doc_id=doc_id,
            filename=os.path.basename(input_dto.file_path),
            status="processing",
            progress=0.0,
            metadata={
                "process_tables": input_dto.process_tables,
                "detect_language": input_dto.detect_language,
                "spell_check": input_dto.spell_check,
                "refine_with_llm": input_dto.refine_with_llm
            }
        )
        
        # Registrar tiempo de inicio
        start_time = time.time()
        
        # Procesar documento
        try:
            # Verificar existencia del archivo
            file_path = Path(input_dto.file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"El archivo no existe: {file_path}")
                
            # Verificar tamaño
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            logger.info(f"Tamaño del archivo: {file_size_mb:.2f} MB")
            
            # Ejecutar caso de uso
            logger.info(f"Ejecutando caso de uso para documento {doc_id}")
            result = use_case.execute(input_dto)
            logger.info(f"Procesamiento completado para documento {doc_id}")
            
        except Exception as process_error:
            # Registrar error detallado
            error_id = log_error_details(
                process_error, 
                f"Error al procesar documento {doc_id}: {input_dto.file_path}"
            )
            
            # Propagar el error con ID para referencia
            raise Exception(f"Error al procesar el documento (Error ID: {error_id}): {str(process_error)}")
        
        # Calcular tiempo de procesamiento
        processing_time = time.time() - start_time
        
        # Actualizar estado a "completed"
        DocumentService.update_document_status(
            doc_id, 
            "completed", 
            100.0, 
            metadata={
                "total_pages": result.total_pages if hasattr(result, 'total_pages') else 0,
                "processing_time": processing_time,
                "language": result.language if hasattr(result, 'language') else "desconocido"
            }
        )
        
        # Registrar éxito en el log de documentos
        log_document_processing(
            doc_id=doc_id,
            filename=os.path.basename(input_dto.file_path),
            status="completed",
            progress=100.0,
            metadata={
                "total_pages": result.total_pages if hasattr(result, 'total_pages') else 0,
                "processing_time": processing_time,
                "language": result.language if hasattr(result, 'language') else "desconocido"
            }
        )
        
        logger.info(f"Documento {doc_id} procesado correctamente en {processing_time:.2f} segundos")
        
    except Exception as e:
        # Registrar error detallado
        error_id = log_error_details(e, f"Error en procesamiento de documento {doc_id}")
        
        # Actualizar estado a "error"
        error_message = f"Error ID: {error_id} - {str(e)}"
        DocumentService.update_document_status(
            doc_id, 
            "error", 
            0.0, 
            error_message=error_message
        )
        
        # Registrar error en el log de documentos
        log_document_processing(
            doc_id=doc_id,
            filename=os.path.basename(input_dto.file_path) if hasattr(input_dto, 'file_path') else "desconocido",
            status="error",
            error=error_message
        )
        
        logger.error(f"Error al procesar documento {doc_id}: {str(e)}")
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

# Rutas para crear y gestionar documentos
@router.post("", response_model=DocumentResponse, responses={400: {"model": ErrorResponse}}, status_code=201)
async def create_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    use_llm: bool = Query(False, description="Usar LLM para refinar el resultado"),
    use_case: PDFToMarkdownUseCase = Depends(get_pdf_to_markdown_use_case)
) -> DocumentResponse:
    """Sube un documento PDF y lo procesa en segundo plano.
    
    Args:
        background_tasks: Tareas en segundo plano
        file: Archivo PDF a procesar
        use_llm: Si se debe usar LLM para refinar el resultado
        use_case: Caso de uso para procesar el documento
        
    Returns:
        DocumentResponse: Información del documento creado
    """
    from infrastructure.logging_setup import logger
    import uuid
    from datetime import datetime
    
    try:
        # Validar el tipo de archivo
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Solo se permiten archivos PDF"
            )
        
        # Crear metadatos del documento
        now = datetime.now().isoformat()
        
        # Preparar opciones de procesamiento
        options = {
            "use_llm": use_llm,
            "process_tables": True,  # Por defecto activado
            "detect_language": True,  # Por defecto activado
            "spell_check": False,  # Por defecto desactivado
        }
        
        # Guardar metadatos usando el método correcto
        doc_id = DocumentService.create_document(file.filename, options)
        
        # Crear ruta de archivo
        file_path = UPLOAD_DIR / f"{doc_id}.pdf"
        
        # Guardar archivo en disco
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Crear DTO para el caso de uso
        input_dto = DocumentInputDTO(
            file_path=str(file_path),
            process_tables=True,  # Por defecto activado
            detect_language=True,  # Por defecto activado
            spell_check=False,  # Por defecto desactivado
            refine_with_llm=use_llm
        )
        
        # Iniciar procesamiento en segundo plano
        background_tasks.add_task(process_document, input_dto, doc_id, use_case)
        
        # Obtener los metadatos del documento recién creado para la respuesta
        document_metadata = DocumentService.get_document(doc_id)
        
        # Devolver respuesta
        return DocumentResponse(
            id=doc_id,
            filename=file.filename,
            status="pending",
            total_pages=0,  # Se actualizará después del procesamiento
            processed_successfully=False,  # Se actualizará después del procesamiento
            created_at=datetime.fromisoformat(document_metadata["created_at"]),
            markdown_url=None,  # Se generará después del procesamiento
            error_message=None
        )
        
    except Exception as e:
        logger.exception(f"Error al procesar documento: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el documento: {str(e)}"
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