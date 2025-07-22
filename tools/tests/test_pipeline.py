from pathlib import Path
from adapters.pymupdf_adapter import extract_tables_markdown
from adapters.ocr_adapter import perform_ocr_on_page
from domain.use_cases import convert_pdf_to_md
import fitz

# PDF de prueba que debe estar en ./pdfs/pdf_escan.pdf
TEST_PDF = Path("pdfs/pdf_escan.pdf")

def test_ocr_extracts_text():
    with fitz.open(TEST_PDF) as doc:
        page = doc[0]
        text = perform_ocr_on_page(page)
        assert isinstance(text, str)
        assert len(text.strip()) > 30, "El OCR devolvió poco o nada de texto"

def test_table_extraction_returns_markdown():
    md = extract_tables_markdown(TEST_PDF)
    assert isinstance(md, str)
    assert "### Table" in md or "| ---" in md, "No se detectaron tablas en el Markdown"

def test_markdown_file_is_saved():
    out_path = convert_pdf_to_md(TEST_PDF)
    assert out_path.exists(), "No se generó el archivo .md"
    assert out_path.name.endswith(".md")
    content = out_path.read_text(encoding="utf-8")
    assert content.startswith("#"), "El archivo .md no comienza con título Markdown"