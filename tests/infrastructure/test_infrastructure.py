"""Tests for infrastructure components."""
import pytest
from pathlib import Path
from infrastructure.logging_setup import configure_logging
from infrastructure.file_storage import save_markdown_file
from infrastructure.ocr_cache import OCRCache

def test_logging_configuration():
    """Test logging setup."""
    logger = configure_logging()
    assert logger is not None
    assert logger.level == 20  # INFO level

def test_markdown_file_storage(tmp_path):
    """Test markdown file storage."""
    content = "# Test Content\n\nSample markdown"
    file_path = tmp_path / "test.md"
    result = save_markdown_file(content, file_path)
    assert Path(result).exists()
    assert Path(result).read_text() == content

@pytest.fixture
def ocr_cache():
    cache = OCRCache()
    yield cache
    # Cleanup after test
    cache.clear()

def test_ocr_cache_operations(ocr_cache):
    """Test OCR cache operations."""
    key = "test_page_1"
    content = "Sample OCR text"
    
    # Test cache miss
    assert ocr_cache.get(key) is None
    
    # Test cache set and hit
    ocr_cache.set(key, content)
    assert ocr_cache.get(key) == content
    
    # Test cache invalidation
    ocr_cache.invalidate(key)
    assert ocr_cache.get(key) is None
