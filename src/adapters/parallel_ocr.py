"""
Parallel OCR helper.

Runs `perform_ocr_on_page` concurrently using a process pool.
"""

from concurrent.futures import ProcessPoolExecutor
from adapters.ocr_adapter import perform_ocr_on_page


def run_parallel(doc):
    """
    Ejecuta OCR en paralelo para cada página de *doc* (fitz.Document).

    Returns
    -------
    list[str]
        Texto OCR de cada página en el mismo orden.
    """
    with ProcessPoolExecutor() as pool:
        return list(pool.map(perform_ocr_on_page, doc))