"""Tests for adapters implementation."""
import pytest
from unittest.mock import Mock, patch
from adapters.ocr_adapter import perform_ocr_on_page
from adapters.llm_refiner import refine_markdown
from adapters.pymupdf_adapter import extract_markdown, extract_tables_markdown
from domain.dtos.content_dtos import TextBlockDTO
from domain.dtos.coordinates_dto import CoordinatesDTO

@pytest.fixture
def mock_page():
    return Mock()

@pytest.fixture
def mock_tesseract():
    with patch('adapters.ocr_adapter.pytesseract') as mock:
        mock.image_to_string.return_value = "Sample OCR text"
        yield mock

def test_ocr_extraction(mock_page, mock_tesseract):
    """Test OCR text extraction."""
    result = perform_ocr_on_page(mock_page)
    assert isinstance(result, str)
    assert len(result) > 0
    mock_tesseract.image_to_string.assert_called_once()

@pytest.mark.integration
def test_table_extraction():
    """Test table extraction from PDF."""
    result = extract_tables_markdown("tests/fixtures/sample.pdf")
    assert isinstance(result, str)
    assert "| " in result  # Basic markdown table check

@pytest.mark.integration
def test_pdf_text_extraction():
    """Test text extraction from PDF."""
    result = extract_markdown("tests/fixtures/sample.pdf")
    assert isinstance(result, str)
    assert len(result) > 0

@patch('adapters.llm_refiner.openai.ChatCompletion.create')
def test_llm_refinement(mock_openai):
    """Test LLM text refinement."""
    mock_openai.return_value = {
        "choices": [{"message": {"content": "Refined text"}}]
    }
    result = refine_markdown("Original text")
    assert result == "Refined text"
    mock_openai.assert_called_once()
