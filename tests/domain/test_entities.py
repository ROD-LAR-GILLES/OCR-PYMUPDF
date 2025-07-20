"""Tests for domain entities and value objects."""
import pytest
from datetime import datetime
from domain.entities.document import Document
from domain.value_objects.page import Page
from domain.value_objects.document_metadata import DocumentMetadata
from domain.value_objects.text_coordinates import TextCoordinates
from domain.value_objects.text_block import TextBlock
from domain.value_objects.table import Table

@pytest.fixture
def sample_coordinates():
    return TextCoordinates(x1=0, y1=0, x2=100, y2=50)

@pytest.fixture
def sample_text_block(sample_coordinates):
    return TextBlock(
        content="Sample text",
        coordinates=sample_coordinates,
        confidence_score=0.95,
        language="es"
    )

@pytest.fixture
def sample_table(sample_coordinates):
    return Table(
        data=[["Header 1", "Header 2"], ["Data 1", "Data 2"]],
        coordinates=sample_coordinates,
        confidence_score=0.9
    )

@pytest.fixture
def sample_page(sample_text_block, sample_table):
    return Page(
        number=1,
        text_blocks=[sample_text_block],
        tables=[sample_table],
        rotation=0,
        has_scanned_content=False,
        confidence_score=0.93
    )

@pytest.fixture
def sample_metadata():
    return DocumentMetadata(
        title="Test Document",
        author="Test Author",
        creation_date=datetime.now(),
        modification_date=datetime.now(),
        producer="Test Producer",
        page_count=1
    )

@pytest.fixture
def sample_document(sample_page, sample_metadata):
    return Document(
        id="test-doc-001",
        path="/test/doc.pdf",
        pages=[sample_page],
        metadata=sample_metadata
    )

def test_document_creation(sample_document):
    """Test document entity creation and properties."""
    assert sample_document.id == "test-doc-001"
    assert sample_document.path == "/test/doc.pdf"
    assert len(sample_document.pages) == 1
    assert not sample_document.has_error
    assert sample_document.total_pages == 1

def test_document_error_handling(sample_document):
    """Test document error handling functionality."""
    sample_document.set_error("Test error")
    assert sample_document.has_error
    assert sample_document.error == "Test error"
    assert not sample_document.processed

def test_page_content(sample_page):
    """Test page value object properties."""
    assert not sample_page.is_empty
    assert sample_page.total_text_blocks == 1
    assert sample_page.total_tables == 1
    assert sample_page.confidence_score == 0.93

def test_text_block_properties(sample_text_block):
    """Test text block value object properties."""
    assert not sample_text_block.is_empty
    assert sample_text_block.word_count == 2
    assert sample_text_block.language == "es"

def test_table_properties(sample_table):
    """Test table value object properties."""
    assert not sample_table.is_empty
    assert sample_table.row_count == 2
    assert sample_table.column_count == 2
