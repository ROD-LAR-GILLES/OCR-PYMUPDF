"""Servicio para gestionar documentos en la API.

Este módulo implementa un servicio para gestionar el estado y procesamiento
de documentos en la API REST.
"""
import json
from pathlib import Path
from datetime import datetime
import uuid
import os
from typing import Dict, List, Optional, Any

# Directorio para almacenar metadatos de documentos
METADATA_DIR = Path("metadata")
METADATA_DIR.mkdir(exist_ok=True)

class DocumentService:
    """Servicio para gestionar documentos y su estado."""
    
    @staticmethod
    def create_document(filename: str, options: Dict[str, Any]) -> str:
        """Crea un nuevo documento en el sistema.
        
        Args:
            filename: Nombre original del archivo
            options: Opciones de procesamiento
            
        Returns:
            str: ID único del documento
        """
        doc_id = str(uuid.uuid4())
        
        # Crear metadatos del documento
        metadata = {
            "id": doc_id,
            "filename": filename,
            "status": "pending",
            "progress": 0.0,
            "created_at": datetime.now().isoformat(),
            "updated_at": None,
            "options": options,
            "error_message": None
        }
        
        # Guardar metadatos
        metadata_path = METADATA_DIR / f"{doc_id}.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        return doc_id
    
    @staticmethod
    def update_document_status(doc_id: str, status: str, progress: float = None, error_message: str = None, metadata: Dict[str, Any] = None):
        """Actualiza el estado de un documento.
        
        Args:
            doc_id: ID único del documento
            status: Nuevo estado (pending, processing, completed, error)
            progress: Progreso del procesamiento (0-100)
            error_message: Mensaje de error si ocurrió alguno
            metadata: Metadatos adicionales para agregar al documento
        """
        metadata_path = METADATA_DIR / f"{doc_id}.json"
        
        if not metadata_path.exists():
            raise FileNotFoundError(f"Documento con ID {doc_id} no encontrado")
        
        # Cargar metadatos actuales
        with open(metadata_path, "r") as f:
            document_metadata = json.load(f)
        
        # Actualizar metadatos
        document_metadata["status"] = status
        document_metadata["updated_at"] = datetime.now().isoformat()
        
        if progress is not None:
            document_metadata["progress"] = progress
        
        if error_message is not None:
            document_metadata["error_message"] = error_message
        
        # Agregar metadatos adicionales si se proporcionan
        if metadata is not None:
            for key, value in metadata.items():
                document_metadata[key] = value
        
        # Guardar metadatos actualizados
        with open(metadata_path, "w") as f:
            json.dump(document_metadata, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def get_document(doc_id: str) -> Dict[str, Any]:
        """Obtiene información de un documento.
        
        Args:
            doc_id: ID único del documento
            
        Returns:
            Dict: Metadatos del documento
        """
        metadata_path = METADATA_DIR / f"{doc_id}.json"
        
        if not metadata_path.exists():
            raise FileNotFoundError(f"Documento con ID {doc_id} no encontrado")
        
        # Cargar metadatos
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        
        return metadata
    
    @staticmethod
    def list_documents(limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Lista los documentos en el sistema.
        
        Args:
            limit: Número máximo de documentos a devolver
            offset: Número de documentos a saltar
            
        Returns:
            List[Dict]: Lista de metadatos de documentos
        """
        documents = []
        
        # Listar archivos de metadatos
        metadata_files = list(METADATA_DIR.glob("*.json"))
        
        # Ordenar por fecha de creación (más recientes primero)
        metadata_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # Aplicar paginación
        paginated_files = metadata_files[offset:offset + limit]
        
        # Cargar metadatos
        for metadata_path in paginated_files:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
                documents.append(metadata)
        
        return documents
    
    @staticmethod
    def delete_document(doc_id: str) -> bool:
        """Elimina un documento y sus metadatos.
        
        Args:
            doc_id: ID único del documento
            
        Returns:
            bool: True si se eliminó correctamente, False si no se encontró
        """
        metadata_path = METADATA_DIR / f"{doc_id}.json"
        
        if not metadata_path.exists():
            return False
        
        # Eliminar metadatos
        os.remove(metadata_path)
        
        # Eliminar archivo original
        upload_dir = Path("uploads")
        for file in upload_dir.glob(f"{doc_id}*"):
            os.remove(file)
        
        # Eliminar resultados
        result_dir = Path("resultado")
        for file in result_dir.glob(f"*{doc_id}*.md"):
            os.remove(file)
        
        return True