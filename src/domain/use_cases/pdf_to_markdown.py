"""Caso de uso para convertir archivos PDF a formato Markdown.

Este módulo implementa la lógica de negocio para convertir documentos PDF a formato Markdown,
utilizando OCR cuando es necesario y refinando el texto con LLM.
"""
from pathlib import Path
from typing import Optional
from domain.ports.document_port import DocumentPort
from domain.ports.storage_port import StoragePort
from domain.ports.llm_port import LLMPort
from domain.dtos.document_dtos import DocumentOutputDTO

class PDFToMarkdownUseCase:
    """Caso de uso para la conversión de PDF a Markdown."""
    
    def __init__(
        self,
        document_port: DocumentPort,
        storage_port: StoragePort,
        llm_port: Optional[LLMPort] = None
    ):
        """
        Inicializa el caso de uso con sus dependencias.

        Args:
            document_port: Puerto para operaciones con documentos
            storage_port: Puerto para almacenamiento
            llm_port: Puerto para refinamiento con LLM (opcional)
        """
        self.document_port = document_port
        self.storage_port = storage_port
        self.llm_port = llm_port

    def execute(self, pdf_path: Path) -> Path:
        """
        Convierte un archivo PDF en un archivo Markdown, utilizando extracción inteligente
        y refinamiento con LLM si está configurado.

        Args:
            pdf_path: Ruta al archivo PDF de entrada.

        Returns:
            Path: Ruta al archivo Markdown generado.
            
        Raises:
            DocumentError: Si hay problemas al procesar el PDF
            StorageError: Si hay problemas al guardar el resultado
            LLMError: Si hay problemas con el refinamiento del texto
        """
        # Extraer contenido del PDF
        markdown_content = self.document_port.extract_markdown(pdf_path)
        
        # Refinar el contenido con LLM solo si está disponible
        if self.llm_port is not None:
            try:
                markdown_content = self.llm_port.refine_text(markdown_content)
            except Exception as e:
                from infrastructure.logging_setup import logger
                logger.warning(f"LLM refinement failed, using raw text: {e}")
        
        # Guardar el resultado
        md_path = self.storage_port.save_markdown(pdf_path.stem, markdown_content)
        return md_path