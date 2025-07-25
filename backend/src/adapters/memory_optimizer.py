"""Optimizador de memoria para procesamiento de documentos grandes.

Implementa estrategias para reducir el consumo de memoria durante
el procesamiento de documentos PDF extensos, incluyendo:
- Procesamiento por lotes de páginas
- Liberación explícita de memoria
- Optimización de imágenes
"""
import gc
import fitz  # PyMuPDF
import logging
from pathlib import Path
from typing import List, Callable, TypeVar, Optional, Iterator
from PIL import Image

T = TypeVar('T')  # Tipo genérico para resultados


class MemoryOptimizer:
    """Optimizador de memoria para procesamiento de documentos grandes."""
    
    def __init__(self, batch_size: int = 5, logger: Optional[logging.Logger] = None):
        """Inicializa el optimizador de memoria.
        
        Args:
            batch_size: Número de páginas a procesar por lote
            logger: Logger opcional para mensajes de diagnóstico
        """
        self.batch_size = batch_size
        self.logger = logger or logging.getLogger(__name__)
    
    def process_document_in_batches(self, pdf_path: Path, page_processor: Callable[[fitz.Page], T]) -> List[T]:
        """Procesa un documento PDF en lotes para optimizar memoria.
        
        Args:
            pdf_path: Ruta al archivo PDF
            page_processor: Función que procesa una página y devuelve un resultado
            
        Returns:
            Lista de resultados por página
        """
        results = []
        total_pages = 0
        
        # Obtener número total de páginas
        with fitz.open(pdf_path) as doc:
            total_pages = doc.page_count
            self.logger.info(f"Documento con {total_pages} páginas, procesando en lotes de {self.batch_size}")
        
        # Procesar por lotes
        for batch_start in range(0, total_pages, self.batch_size):
            batch_end = min(batch_start + self.batch_size, total_pages)
            batch_results = self._process_batch(pdf_path, batch_start, batch_end, page_processor)
            results.extend(batch_results)
            
            # Forzar liberación de memoria
            self._force_gc()
            
            progress = (batch_end / total_pages) * 100
            self.logger.info(f"Progreso: {progress:.1f}% ({batch_end}/{total_pages} páginas)")
        
        return results
    
    def _process_batch(self, pdf_path: Path, start_page: int, end_page: int, 
                      page_processor: Callable[[fitz.Page], T]) -> List[T]:
        """Procesa un lote de páginas.
        
        Args:
            pdf_path: Ruta al archivo PDF
            start_page: Índice de página inicial (inclusive)
            end_page: Índice de página final (exclusive)
            page_processor: Función que procesa una página
            
        Returns:
            Lista de resultados para este lote
        """
        batch_results = []
        
        with fitz.open(pdf_path) as doc:
            for page_idx in range(start_page, end_page):
                page = doc.load_page(page_idx)
                result = page_processor(page)
                batch_results.append(result)
                
                # Liberar página explícitamente
                page = None
        
        return batch_results
    
    def optimize_image(self, image: Image.Image, max_size: int = 1500) -> Image.Image:
        """Optimiza una imagen para reducir consumo de memoria.
        
        Args:
            image: Imagen a optimizar
            max_size: Tamaño máximo (ancho o alto) en píxeles
            
        Returns:
            Imagen optimizada
        """
        width, height = image.size
        
        # Redimensionar si es demasiado grande
        if width > max_size or height > max_size:
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
            
            image = image.resize((new_width, new_height), Image.LANCZOS)
            self.logger.debug(f"Imagen redimensionada de {width}x{height} a {new_width}x{new_height}")
        
        return image
    
    def _force_gc(self) -> None:
        """Fuerza la recolección de basura para liberar memoria."""
        gc.collect()