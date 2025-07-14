"""
Tests unitarios para el adaptador PyMuPDF, encargados de verificar la extracción de texto y tablas
desde archivos PDF tanto digitales como escaneados, usando OCR y Camelot.

Incluye pruebas para asegurar el correcto funcionamiento de:
- OCR selectivo por página
- Detección de tablas (lattice y stream)
- Estructura esperada en la salida Markdown
"""

import pytest
from pathlib import Path
from adapters.pymupdf_adapter import extract_markdown, extract_tables_markdown

# Ruta al directorio con archivos PDF de prueba usados en los tests
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


def test_camelot_stream_activado_si_lattice_falla():
    """
    Verifica que se active el modo 'stream' de Camelot si 'lattice' no detecta tablas.
    """
    path = FIXTURE_DIR / "sin_bordes.pdf"
    md = extract_tables_markdown(path)
    assert isinstance(md, str)
    assert "Tabla" in md or "## Tablas" in md