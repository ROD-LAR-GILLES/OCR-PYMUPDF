"""Tests for interface components."""
import pytest
from pathlib import Path
from unittest.mock import patch, Mock
from interfaces.cli_menu import process_pdf_file, show_menu, _compare_pdfs
from domain.dtos.document_dtos import DocumentInputDTO, DocumentOutputDTO, DocumentComparisonDTO
from domain.use_cases.document_comparison import DocumentComparisonUseCase

@pytest.fixture
def mock_use_case():
    return Mock()

def test_menu_display():
    """Test menu display functionality."""
    with patch('builtins.print') as mock_print:
        show_menu()
        assert mock_print.call_count > 0

def test_process_pdf_valid_file(mock_use_case):
    """Test PDF processing with valid file."""
    input_dto = DocumentInputDTO(
        file_path="test.pdf",
        process_tables=True
    )
    mock_use_case.execute.return_value = DocumentOutputDTO(
        id="test-001",
        file_path="test.pdf",
        total_pages=1,
        processed_successfully=True
    )
    
    result = process_pdf_file(input_dto, mock_use_case)
    assert result.processed_successfully
    mock_use_case.execute.assert_called_once_with(input_dto)

def test_process_pdf_invalid_file(mock_use_case):
    """Test PDF processing with invalid file."""
    input_dto = DocumentInputDTO(
        file_path="nonexistent.pdf",
        process_tables=True
    )
    mock_use_case.execute.side_effect = FileNotFoundError()
    
    with pytest.raises(FileNotFoundError):
        process_pdf_file(input_dto, mock_use_case)

@patch('builtins.input', side_effect=['4'])  # Simula selección de salir
def test_menu_exit(mock_input):
    """Test menu exit option."""
    result = show_menu()
    assert result is False  # Menu should return False when exiting

@patch('interfaces.cli_menu.select_pdf', side_effect=['original.pdf', 'new.pdf'])
@patch('interfaces.cli_menu.PyMuPDFAdapter')
@patch('interfaces.cli_menu.FileStorage')
@patch('interfaces.cli_menu.DocumentComparisonUseCase')
def test_compare_pdfs_success(mock_use_case_class, mock_storage_class, mock_adapter_class, mock_select_pdf):
    """Test document comparison functionality with successful execution."""
    # Configurar mocks
    mock_adapter = Mock()
    mock_storage = Mock()
    mock_use_case = Mock()
    
    mock_adapter_class.return_value = mock_adapter
    mock_storage_class.return_value = mock_storage
    mock_use_case_class.return_value = mock_use_case
    
    # Configurar resultado simulado
    mock_result = DocumentComparisonDTO(
        original_path="original.pdf",
        new_path="new.pdf",
        original_pages=2,
        new_pages=3,
        report_path="output/comparison_report.md"
    )
    mock_use_case.execute.return_value = mock_result
    
    # Ejecutar la función
    with patch('builtins.print') as mock_print:
        _compare_pdfs()
    
    # Verificar que se creó el caso de uso correctamente
    mock_use_case_class.assert_called_once_with(
        document_port=mock_adapter,
        storage_port=mock_storage
    )
    
    # Verificar que se ejecutó el caso de uso
    mock_use_case.execute.assert_called_once()
    
    # Verificar que se mostró el resultado
    mock_print.assert_any_call("\n[OK] Informe de comparación generado: output/comparison_report.md")

@patch('interfaces.cli_menu.select_pdf', side_effect=[None, 'new.pdf'])
def test_compare_pdfs_no_original(mock_select_pdf):
    """Test document comparison with no original PDF selected."""
    with patch('builtins.print') as mock_print:
        _compare_pdfs()
    
    # Verificar que la función termina temprano
    mock_select_pdf.assert_called_once()

@patch('interfaces.cli_menu.select_pdf', side_effect=['original.pdf', None])
def test_compare_pdfs_no_new(mock_select_pdf):
    """Test document comparison with no new PDF selected."""
    with patch('builtins.print') as mock_print:
        _compare_pdfs()
    
    # Verificar que la función termina después de la segunda selección
    assert mock_select_pdf.call_count == 2

@patch('interfaces.cli_menu.select_pdf', side_effect=['original.pdf', 'new.pdf'])
@patch('interfaces.cli_menu.PyMuPDFAdapter')
@patch('interfaces.cli_menu.FileStorage')
@patch('interfaces.cli_menu.DocumentComparisonUseCase')
def test_compare_pdfs_error(mock_use_case_class, mock_storage_class, mock_adapter_class, mock_select_pdf):
    """Test document comparison with error during execution."""
    # Configurar mocks
    mock_adapter = Mock()
    mock_storage = Mock()
    mock_use_case = Mock()
    
    mock_adapter_class.return_value = mock_adapter
    mock_storage_class.return_value = mock_storage
    mock_use_case_class.return_value = mock_use_case
    
    # Configurar error simulado
    mock_use_case.execute.side_effect = Exception("Test error")
    
    # Ejecutar la función
    with patch('builtins.print') as mock_print:
        _compare_pdfs()
    
    # Verificar que se mostró el error
    mock_print.assert_any_call("[Error] Error al comparar documentos: Test error")
