# tests/test_digital_pdfs.py

import pytest
from pathlib import Path
from adapters.pymupdf_adapter import extract_tables_markdown, extract_markdown


# ──────────────────────────────
#         Fixtures y Paths
# ──────────────────────────────
FIXTURE_DIR = Path("tests/fixtures")
DIGITAL_PDF = FIXTURE_DIR / "digital.pdf"


# ──────────────────────────────
#           Tests
# ──────────────────────────────
def test_camelot_extraction_on_embedded_table():
    """
    Verifica que Camelot extraiga al menos una tabla desde PDF digital.
    """
    md = extract_tables_markdown(DIGITAL_PDF)
    assert isinstance(md, str)
    assert "### Table" in md or "| ---" in md, "No se detectaron tablas en el Markdown"


def test_digital_pdf_extraction_no_ocr(monkeypatch):
    """
    Verifica que un PDF digital no active OCR innecesario.
    """
    from adapters import ocr_adapter

    called = False

    def fake_perform_ocr_on_page(page):
        nonlocal called
        called = True
        return "Texto simulado"

    monkeypatch.setattr("adapters.ocr_adapter.perform_ocr_on_page", fake_perform_ocr_on_page)

    extract_markdown(DIGITAL_PDF)
    assert not called, "OCR fue ejecutado en un PDF digital"