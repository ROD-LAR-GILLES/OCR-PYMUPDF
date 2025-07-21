"""DTOs for document-related data transfer between layers."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

@dataclass
class DocumentInputDTO:
    """DTO for incoming document data from the presentation layer."""
    
    file_path: str
    process_tables: bool = False
    detect_language: bool = False
    spell_check: bool = False
    refine_with_llm: bool = False

@dataclass
class DocumentOutputDTO:
    """DTO for outgoing document data to the presentation layer."""
    
    id: str
    file_path: str
    total_pages: int
    processed_successfully: bool
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    creation_date: Optional[datetime] = None
    author: Optional[str] = None

@dataclass
class DocumentMetadataDTO:
    """DTO for document metadata."""
    
    title: Optional[str] = None
    author: Optional[str] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    producer: Optional[str] = None
    subject: Optional[str] = None
    creator: Optional[str] = None
    page_count: int = 0


@dataclass
class DocumentDiffDTO:
    """DTO para diferencias entre documentos a nivel de página."""
    page_number: int
    additions: int = 0
    deletions: int = 0
    changes: int = 0
    diff_text: str = ""


@dataclass
class DocumentComparisonDTO:
    """DTO para resultados de comparación entre documentos."""
    original_path: str
    new_path: str
    original_pages: int
    new_pages: int
    page_differences: List[DocumentDiffDTO] = field(default_factory=list)
    metadata_changes: Dict[str, Tuple[str, str]] = field(default_factory=dict)
    report_path: Optional[str] = None
