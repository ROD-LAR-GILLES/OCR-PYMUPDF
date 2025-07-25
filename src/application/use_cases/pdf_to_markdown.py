"""
Caso de uso para convertir archivos PDF a formato Markdown.

Este módulo implementa la lógica de negocio para convertir documentos PDF a formato Markdown,
utilizando OCR cuando es necesario y refinando el texto con LLM.
"""
from pathlib import Path
from typing import Protocol
from domain.ports.document_port import DocumentPort
from domain.ports.storage_port import StoragePort
from domain.ports.llm_port import LLMPort

class PDFToMarkdownUseCase:
    """Caso de uso para la conversión de PDF a Markdown."""
    
    def __init__(
        self,
        document_port: DocumentPort,
        storage_port: StoragePort,
        llm_port: LLMPort
    ):
        """
        Inicializa el caso de uso con sus dependencias.

        Args:
            document_port: Puerto para operaciones con documentos
            storage_port: Puerto para almacenamiento
            llm_port: Puerto para refinamiento con LLM
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
        from infrastructure.logging_setup import logger, log_error_details
        
        logger.info(f"Iniciando conversión de PDF a Markdown: {pdf_path}")
        
        try:
            # Verificar que el archivo existe
            if not pdf_path.exists():
                error_msg = f"El archivo PDF no existe: {pdf_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
                
            # Registrar información del archivo
            file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
            logger.info(f"Archivo PDF: {pdf_path.name}, Tamaño: {file_size_mb:.2f} MB")
            
            # Extraer contenido del PDF
            logger.info("Extrayendo contenido del PDF")
            try:
                markdown_content = self.document_port.extract_markdown(pdf_path)
                logger.info(f"Extracción completada: {len(markdown_content)} caracteres")
            except Exception as doc_error:
                logger.error(f"Error al extraer contenido del PDF: {doc_error}")
                log_error_details(doc_error, f"Extracción de contenido de {pdf_path}")
                raise
            
            # Refinar el contenido con LLM solo si está disponible
            if self.llm_port is not None:
                try:
                    logger.info("Iniciando refinamiento con LLM")
                    markdown_content = self.llm_port.format_markdown(markdown_content)
                    logger.info("Refinamiento con LLM completado")
                except Exception as llm_error:
                    logger.warning(f"LLM refinement failed, using raw text: {llm_error}")
                    log_error_details(llm_error, "Refinamiento LLM")
            
            # Guardar el resultado
            try:
                logger.info(f"Guardando resultado para {pdf_path.stem}")
                md_path = self.storage_port.save_markdown(pdf_path.stem, markdown_content)
                logger.info(f"Archivo Markdown guardado en: {md_path}")
                return md_path
            except Exception as storage_error:
                logger.error(f"Error al guardar el archivo Markdown: {storage_error}")
                log_error_details(storage_error, f"Guardando resultado para {pdf_path.stem}")
                raise
                
        except Exception as e:
            logger.error(f"Error en la conversión de PDF a Markdown: {e}")
            log_error_details(e, f"Conversión de {pdf_path} a Markdown")
            raise
