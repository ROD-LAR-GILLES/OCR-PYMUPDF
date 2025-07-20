"""Tests for interface components."""
import pytest
from unittest.mock import patch, Mock
from interfaces.cli_menu import process_pdf_file, show_menu
from domain.dtos.document_dtos import DocumentInputDTO, DocumentOutputDTO

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
