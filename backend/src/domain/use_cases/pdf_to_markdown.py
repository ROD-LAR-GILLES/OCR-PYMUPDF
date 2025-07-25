from pathlib import Path
from typing import Optional
from domain.ports.document_port import DocumentPort
from domain.ports.storage_port import StoragePort
from domain.ports.llm_port import LLMPort
from domain.dtos.document_dtos import DocumentInputDTO, DocumentOutputDTO

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

    def execute(self, input_dto: DocumentInputDTO) -> DocumentOutputDTO:
        """
        Convierte un archivo PDF en un archivo Markdown, utilizando extracción inteligente
        y refinamiento con LLM si está configurado.

        Args:
            input_dto: DTO con la información del documento a procesar

        Returns:
            DocumentOutputDTO: DTO con la información del documento procesado
            
        Raises:
            DocumentError: Si hay problemas al procesar el PDF
            StorageError: Si hay problemas al guardar el resultado
            LLMError: Si hay problemas con el refinamiento del texto
        """
        from infrastructure.logging_setup import logger, log_error_details
        
        logger.info(f"Iniciando conversión de PDF a Markdown: {input_dto.file_path}")
        pdf_path = Path(input_dto.file_path)
        
        # Verificar si se debe usar refinamiento LLM
        should_use_llm = self.llm_port is not None and input_dto.refine_with_llm
        if input_dto.refine_with_llm and self.llm_port is None:
            logger.warning("Se solicitó refinamiento LLM pero no hay proveedor LLM disponible")
            logger.info("Continuando con procesamiento OCR estándar sin refinamiento LLM")
        
        try:
            # Verificar que el archivo existe
            if not pdf_path.exists():
                error_msg = f"El archivo PDF no existe: {pdf_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            # Verificar que el archivo es accesible
            try:
                with open(pdf_path, 'rb') as f:
                    pass
            except PermissionError as pe:
                logger.error(f"No se tienen permisos para acceder al archivo: {pdf_path}")
                log_error_details(pe, f"Error de permisos en {pdf_path}")
                raise
            
            # Registrar información del archivo
            file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
            logger.info(f"Tamaño del archivo PDF: {file_size_mb:.2f} MB")
            
            # Extraer contenido del PDF
            logger.info(f"Extrayendo contenido del PDF: {pdf_path}")
            try:
                markdown_content = self.document_port.extract_markdown(pdf_path)
                logger.info(f"Extracción completada. Longitud del contenido: {len(markdown_content)} caracteres")
            except Exception as extract_error:
                logger.error(f"Error al extraer contenido del PDF: {extract_error}")
                log_error_details(extract_error, f"Extracción de contenido de {pdf_path}")
                raise
            
            # Refinar el contenido con LLM solo si está disponible y se solicita
            if should_use_llm:
                logger.info("Iniciando refinamiento con LLM")
                try:
                    refined_content = self.llm_port.refine_text(markdown_content)
                    markdown_content = refined_content
                    logger.info("Refinamiento con LLM completado exitosamente")
                except Exception as llm_error:
                    logger.warning(f"Falló el refinamiento con LLM, usando texto original: {llm_error}")
                    log_error_details(llm_error, "Refinamiento LLM")
            
            # Guardar el resultado
            logger.info(f"Guardando resultado para {pdf_path.stem}")
            try:
                md_path = self.storage_port.save_markdown(pdf_path.stem, markdown_content)
                logger.info(f"Archivo Markdown guardado en: {md_path}")
            except Exception as storage_error:
                logger.error(f"Error al guardar el archivo Markdown: {storage_error}")
                log_error_details(storage_error, f"Guardando resultado para {pdf_path.stem}")
                raise
            
            # Obtener metadatos del documento
            try:
                metadata = self.document_port.extract_metadata(pdf_path)
                logger.info(f"Metadatos extraídos: {metadata}")
            except Exception as metadata_error:
                logger.warning(f"Error al extraer metadatos: {metadata_error}")
                metadata = None
                
            # Crear y retornar DTO de salida
            output_dto = DocumentOutputDTO(
                id=input_dto.file_path.split('/')[-1].split('_')[0],  # Extraer ID del nombre del archivo
                file_path=str(pdf_path),
                total_pages=metadata.page_count if metadata else 1,
                processed_successfully=True,
                creation_date=metadata.creation_date if metadata else None,
                author=metadata.author if metadata else None,
                processing_time=None  # Se actualiza después en el proceso
            )
            
            logger.info(f"Procesamiento completado para {pdf_path}")
            return output_dto
            
        except Exception as e:
            logger.error(f"Error en conversión de PDF a Markdown: {e}")
            log_error_details(e, f"Conversión de {pdf_path} a Markdown")
            raise