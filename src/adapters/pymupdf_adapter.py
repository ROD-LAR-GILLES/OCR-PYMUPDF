"""
PDF‑to‑Markdown adapter.

• Uses PyMuPDF (fitz) to extract embedded text from digital PDFs.
• Falls back to selective OCR (see ``ocr_adapter``) when pages have no selectable text.
• Table extraction workflow:
    1. Render each page to an image (``_RENDER_DPI``).
    2. Visually detect pages with table‑like structures.
    3. Run Camelot ―first *lattice*, then *stream*― on those pages.
    4. If Camelot finds nothing, fall back to pdfplumber.

This module resides in the *infrastructure* layer of the clean architecture,
serving as a bridge between domain logic and external libraries.
"""

from __future__ import annotations
import io
from pathlib import Path
from typing import List
import camelot
import fitz
import pdfplumber
from PIL import Image
from loguru import logger
from tabulate import tabulate

from adapters.ocr_adapter import has_visual_table, needs_ocr, perform_ocr_on_page


# DPI used when rendering pages to images
_RENDER_DPI = 300


# ───────────────────────── Table extraction ──────────────────────────
def extract_tables_markdown(pdf_path: Path) -> str:
    """
    Extracts visually detected tables from *pdf_path* and returns them in Markdown.

    Steps
    -----
    1. Render every page at ``_RENDER_DPI`` DPI.
    2. Skip pages that do not appear tabular (fast visual check).
    3. On table pages run Camelot: lattice, then stream.
    4. If Camelot fails, use pdfplumber as fallback.

    Returns
    -------
    str
        Concatenated Markdown for all tables (empty if none found).
    """
    md_parts: List[str] = []

    try:
        with fitz.open(pdf_path) as doc:
            for page_num, page in enumerate(doc, start=1):
                # Render page to PIL
                pix = page.get_pixmap(dpi=_RENDER_DPI, alpha=False)
                img = Image.open(io.BytesIO(pix.tobytes("png")))

                # Quick visual gate
                if not has_visual_table(img):
                    logger.debug(f"[Page {page_num}] No table structure detected — skipping")
                    continue

                logger.info(f"[Page {page_num}] Table detected visually — running Camelot")

                # Camelot — lattice → stream
                try:
                    tables = camelot.read_pdf(str(pdf_path), pages=str(page_num), flavor="lattice")
                    if tables.n == 0:
                        logger.debug(f"[Page {page_num}] lattice found none — trying stream")
                        tables = camelot.read_pdf(str(pdf_path), pages=str(page_num), flavor="stream")

                    if tables.n:
                        md_parts.append(f"## Tables (Camelot · page {page_num})\n")
                        for idx, table in enumerate(tables, start=1):
                            md_parts.append(f"### Table {idx}\n\n{table.df.to_markdown()}\n")
                        continue
                except Exception as exc:  # noqa: BLE001
                    logger.warning(f"[Page {page_num}] Camelot error → {exc}")

                # pdfplumber fallback
                try:
                    with pdfplumber.open(pdf_path) as pdf_pl:
                        pg = pdf_pl.pages[page_num - 1]
                        tbls = pg.extract_tables()
                        if tbls:
                            md_parts.append(f"## Tables (pdfplumber · page {page_num})\n")
                            for idx, tbl in enumerate(tbls, start=1):
                                md_parts.append(
                                    f"### Table {idx}\n\n{tabulate(tbl, tablefmt='pipe')}\n"
                                )
                except Exception as exc:  # noqa: BLE001
                    logger.warning(f"[Page {page_num}] pdfplumber error → {exc}")

    except Exception as exc:  # noqa: BLE001
        logger.error(f"Table extraction failed for {pdf_path} → {exc}")

    return "\n".join(md_parts)


# ─────────────────────── Full‑document extraction ───────────────────────
def extract_markdown(pdf_path: Path) -> str:
    """
    Convert an entire PDF to Markdown, applying OCR selectively.

    • If ``needs_ocr(page)`` is True → run OCR on that page.
    • Else, extract embedded text with PyMuPDF.

    The final Markdown includes:
    • A top‑level title (file stem).
    • One section per page.
    • A table appendix, if tables were found.
    """
    logger.info(f"Processing {pdf_path} …")
    page_parts: List[str] = []

    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc, start=1):
            if needs_ocr(page):
                logger.info(f"[Page {page_num}] No embedded text — running OCR")
                text = perform_ocr_on_page(page)
            else:
                logger.debug(f"[Page {page_num}] Extracting embedded text")
                text = page.get_text("text")
                # Para diagnóstico: visualizamos bloques detectados (layoutparser)
            page_parts.append(f"## Page {page_num}\n\n{text.strip()}")

    md_out = f"# {pdf_path.stem}\n\n" + "\n\n".join(page_parts)

    tables_md = extract_tables_markdown(pdf_path)
    if tables_md:
        md_out += "\n\n" + tables_md

    return md_out