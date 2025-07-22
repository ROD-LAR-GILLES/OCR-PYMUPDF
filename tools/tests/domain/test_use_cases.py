"""Tests for domain use cases."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from domain.use_cases.document_comparison import DocumentComparisonUseCase
from domain.dtos.document_dtos import DocumentComparisonDTO, DocumentDiffDTO, DocumentMetadataDTO

@pytest.fixture
def mock_document_port():
    mock = Mock()
    # Configurar el comportamiento del puerto de documento simulado
    mock.extract_pages.side_effect = [
        # Páginas del documento original
        ["Página 1 original", "Página 2 original"],
        # Páginas del documento nuevo
        ["Página 1 modificada", "Página 2 original", "Página 3 nueva"]
    ]
    
    # Configurar metadatos simulados
    original_metadata = DocumentMetadataDTO(
        title="Documento Original",
        author="Autor Original",
        creation_date=datetime(2023, 1, 1),
        modification_date=datetime(2023, 1, 1),
        producer="Producer Original",
        page_count=2
    )
    
    new_metadata = DocumentMetadataDTO(
        title="Documento Modificado",
        author="Autor Original",
        creation_date=datetime(2023, 1, 1),
        modification_date=datetime(2023, 2, 1),
        producer="Producer Nuevo",
        page_count=3
    )
    
    mock.extract_metadata.side_effect = [original_metadata, new_metadata]
    return mock

@pytest.fixture
def mock_storage_port():
    mock = Mock()
    mock.save_markdown.return_value = Path("/output/comparison_report.md")
    return mock

@pytest.fixture
def comparison_use_case(mock_document_port, mock_storage_port):
    return DocumentComparisonUseCase(
        document_port=mock_document_port,
        storage_port=mock_storage_port
    )

def test_document_comparison_execution(comparison_use_case):
    """Test document comparison use case execution."""
    # Ejecutar el caso de uso
    result = comparison_use_case.execute(
        original_pdf_path=Path("/test/original.pdf"),
        new_pdf_path=Path("/test/new.pdf"),
        output_path=Path("/output/comparison_report.md")
    )
    
    # Verificar que el resultado es del tipo correcto
    assert isinstance(result, DocumentComparisonDTO)
    
    # Verificar que se extrajeron las páginas de ambos documentos
    comparison_use_case.document_port.extract_pages.assert_any_call(Path("/test/original.pdf"))
    comparison_use_case.document_port.extract_pages.assert_any_call(Path("/test/new.pdf"))
    
    # Verificar que se extrajeron los metadatos de ambos documentos
    comparison_use_case.document_port.extract_metadata.assert_any_call(Path("/test/original.pdf"))
    comparison_use_case.document_port.extract_metadata.assert_any_call(Path("/test/new.pdf"))
    
    # Verificar que se guardó el informe
    comparison_use_case.storage_port.save_markdown.assert_called_once()
    
    # Verificar los datos del resultado
    assert result.original_path == "/test/original.pdf"
    assert result.new_path == "/test/new.pdf"
    assert result.original_pages == 2
    assert result.new_pages == 3
    assert result.report_path == "/output/comparison_report.md"

def test_document_comparison_differences(comparison_use_case):
    """Test document comparison differences detection."""
    # Ejecutar el caso de uso
    result = comparison_use_case.execute(
        original_pdf_path=Path("/test/original.pdf"),
        new_pdf_path=Path("/test/new.pdf")
    )
    
    # Verificar que se detectaron las diferencias en las páginas
    assert len(result.page_differences) > 0
    
    # Verificar que la primera página tiene diferencias
    page_1_diff = next((diff for diff in result.page_differences if diff.page_number == 1), None)
    assert page_1_diff is not None
    assert page_1_diff.additions > 0 or page_1_diff.deletions > 0 or page_1_diff.changes > 0
    
    # Verificar que se detectó la página nueva
    page_3_diff = next((diff for diff in result.page_differences if diff.page_number == 3), None)
    assert page_3_diff is not None
    assert page_3_diff.additions > 0
    
    # Verificar que se detectaron los cambios en metadatos
    assert len(result.metadata_changes) > 0
    assert "title" in result.metadata_changes
    assert "modification_date" in result.metadata_changes
    assert "producer" in result.metadata_changes
    assert "author" not in result.metadata_changes  # No cambió

def test_document_comparison_no_output_path(comparison_use_case):
    """Test document comparison without output path."""
    # Ejecutar el caso de uso sin especificar ruta de salida
    result = comparison_use_case.execute(
        original_pdf_path=Path("/test/original.pdf"),
        new_pdf_path=Path("/test/new.pdf")
    )
    
    # Verificar que no se guardó ningún informe
    comparison_use_case.storage_port.save_markdown.assert_not_called()
    
    # Verificar que el campo report_path es None
    assert result.report_path is None

def test_normalize_text_method(comparison_use_case):
    """Test text normalization method."""
    # Texto con espacios múltiples y en los extremos
    text = "  Este  es un   texto   con    espacios   múltiples  "
    
    # Normalizar el texto
    normalized = comparison_use_case._normalize_text(text)
    
    # Verificar que se eliminaron los espacios múltiples y en los extremos
    assert normalized == "Este es un texto con espacios múltiples"
    assert "  " not in normalized
    assert not normalized.startswith(" ")
    assert not normalized.endswith(" ")

def test_generate_markdown_report(comparison_use_case):
    """Test markdown report generation."""
    # Crear un DTO de comparación simulado
    comparison = DocumentComparisonDTO(
        original_path="/test/original.pdf",
        new_path="/test/new.pdf",
        original_pages=2,
        new_pages=3,
        page_differences=[
            DocumentDiffDTO(
                page_number=1,
                additions=5,
                deletions=2,
                changes=1,
                diff_text="+ Línea añadida\n- Línea eliminada\n? Línea cambiada"
            )
        ],
        metadata_changes={
            "title": ("Documento Original", "Documento Modificado"),
            "modification_date": ("2023-01-01", "2023-02-01")
        }
    )
    
    # Generar el informe
    report = comparison_use_case._generate_markdown_report(comparison)
    
    # Verificar que el informe contiene las secciones esperadas
    assert "# Informe de Comparación de Documentos" in report
    assert "## Resumen" in report
    assert "## Cambios en Metadatos" in report
    assert "## Diferencias por Página" in report
    assert "### Página 1" in report
    
    # Verificar que el informe contiene los datos esperados
    assert "/test/original.pdf" in report
    assert "/test/new.pdf" in report
    assert "Documento Original" in report
    assert "Documento Modificado" in report
    assert "```diff" in report
    assert "+ Línea añadida" in report