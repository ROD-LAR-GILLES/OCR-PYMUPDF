"""Modelos de datos para la API REST.

Este módulo define los modelos de datos utilizados en la API REST,
implementados con Pydantic para validación y serialización.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DocumentBase(BaseModel):
    """Modelo base para documentos."""
    id: str = Field(..., description="ID único del documento")
    filename: str = Field(..., description="Nombre original del archivo")

class DocumentStatus(DocumentBase):
    """Estado de procesamiento de un documento."""
    status: str = Field(..., description="Estado del procesamiento (pending, processing, completed, error)")
    progress: float = Field(0.0, description="Progreso del procesamiento (0-100)")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Última actualización")
    error_message: Optional[str] = Field(None, description="Mensaje de error si ocurrió alguno")

class DocumentCreate(BaseModel):
    """Datos para crear un nuevo documento."""
    use_llm: bool = Field(False, description="Si se debe usar LLM para refinar el texto")
    process_tables: bool = Field(True, description="Si se deben procesar tablas")
    detect_language: bool = Field(True, description="Si se debe detectar el idioma")
    spell_check: bool = Field(True, description="Si se debe realizar corrección ortográfica")

class DocumentResponse(DocumentBase):
    """Respuesta con información del documento."""
    total_pages: int = Field(0, description="Número total de páginas")
    processed_successfully: bool = Field(False, description="Si el documento se procesó correctamente")
    processing_time: Optional[float] = Field(None, description="Tiempo de procesamiento en segundos")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    markdown_url: Optional[str] = Field(None, description="URL para descargar el Markdown")
    error_message: Optional[str] = Field(None, description="Mensaje de error si ocurrió alguno")

class PageInfo(BaseModel):
    """Información sobre una página del documento."""
    page_number: int = Field(..., description="Número de página")
    has_text: bool = Field(True, description="Si la página contiene texto")
    has_tables: bool = Field(False, description="Si la página contiene tablas")
    is_scanned: bool = Field(False, description="Si la página es escaneada")
    confidence_score: Optional[float] = Field(None, description="Puntuación de confianza del OCR")

class DocumentDetail(DocumentResponse):
    """Información detallada de un documento."""
    pages: List[PageInfo] = Field(default_factory=list, description="Información de las páginas")
    author: Optional[str] = Field(None, description="Autor del documento")
    creation_date: Optional[datetime] = Field(None, description="Fecha de creación del documento original")
    language: Optional[str] = Field(None, description="Idioma detectado")

class ErrorResponse(BaseModel):
    """Respuesta de error."""
    detail: str = Field(..., description="Mensaje de error")