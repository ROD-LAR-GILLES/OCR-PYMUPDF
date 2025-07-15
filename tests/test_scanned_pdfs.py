# tests/test_scanned_pdfs.py
from adapters.pymupdf_adapter import extract_tables_markdown, extract_markdown
from pathlib import Path

FIXTURE_DIR = Path("tests/fixtures")
SCANNED_PDF = FIXTURE_DIR / "scanned.pdf"

def test_ocr_runs_on_scanned_page(monkeypatch):
    """Verifica que OCR se ejecute en documentos escaneados."""
    from adapters import ocr_adapter

    called = False
    def fake_perform_ocr_on_page(page):
        nonlocal called
        called = True
        return "Texto OCR"

    monkeypatch.setattr(ocr_adapter, "perform_ocr_on_page", fake_perform_ocr_on_page)
    extract_markdown(SCANNED_PDF)
    assert called, "OCR no fue ejecutado en PDF escaneado"

def test_detected_table_regions_return_markdown():
    """Verifica que al menos una tabla sea detectada por fallback OCR."""
    md = extract_tables_markdown(SCANNED_PDF)
    assert isinstance(md, str)
    assert "### Table" in md or "| ---" in md, "No se detectaron tablas en el Markdown"