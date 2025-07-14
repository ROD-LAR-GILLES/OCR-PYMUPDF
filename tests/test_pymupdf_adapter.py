import pytest
from pathlib import Path
from adapters.pymupdf_adapter import extract_markdown, extract_tables_markdown

FIXTURE_DIR = Path(__file__).parent / "fixtures"

@pytest.mark.parametrize("pdf_name", ["digital.pdf", "scanned.pdf"])
def test_extract_markdown(pdf_name):
    path = FIXTURE_DIR / pdf_name
    md = extract_markdown(path)
    assert isinstance(md, str)
    assert md.startswith("# "), "El Markdown debe comenzar con un título"
    assert "Página 1" in md, "Debe incluir al menos una sección de página"

def test_extract_tables_markdown():
    path = FIXTURE_DIR / "tables.pdf"
    md_tables = extract_tables_markdown(path)
    assert isinstance(md_tables, str)
    # Si no hay tablas, md_tables puede ser vacío; si las hay, debe contener 'Tabla'
    assert md_tables == "" or "Tabla" in md_tables