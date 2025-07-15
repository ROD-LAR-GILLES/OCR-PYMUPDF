"""
PDF-to-Markdown adapter.

• Uses PyMuPDF (fitz) to extract embedded text from digital PDFs.
• Falls back to selective OCR (see ``ocr_adapter``) when pages have no selectable text.
• Table extraction workflow:
    1. Render each page to an image (``_RENDER_DPI``).
    2. Visually detect pages with table-like structures.
    3. Run Camelot ―first *lattice*, then *stream*― on those pages.
    4. If Camelot fails, fall back to pdfplumber.

This module resides in the *infrastructure* layer of the clean architecture,
serving as a bridge between domain logic and external libraries.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import List

# ──────── External imports ────────
import camelot
import fitz
import pdfplumber
from PIL import Image
from loguru import logger
from tabulate import tabulate

# ──────── Internal adapters ────────
import adapters.ocr_adapter as ocr_adapter

# ──────── Configuración ────────
_RENDER_DPI = 300


###############################################################################
#                      FULL DOCUMENT EXTRACTION FLOW                          #
###############################################################################

def extract_markdown(pdf_path: Path) -> str:
    """
    Convert an entire PDF to Markdown, applying OCR selectively.

    • If ``needs_ocr(page)`` is True → run OCR on that page.
    • Else, extract embedded text with PyMuPDF.

    The final Markdown includes:
    • A top-level title (file stem).
    • One section per page.
    • A table appendix, if tables were found.
    """
    logger.info(f"Processing {pdf_path} …")
    page_parts: List[str] = []

    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc, start=1):
            if ocr_adapter.needs_ocr(page):
                logger.info(f"[Page {page_num}] No embedded text — running OCR")
                text = ocr_adapter.perform_ocr_on_page(page)
            else:
                logger.debug(f"[Page {page_num}] Extracting embedded text")
                raw = page.get_text("text")
                text = ocr_adapter.detect_lists(ocr_adapter._cleanup_text(raw))

            page_parts.append(f"## Page {page_num}\n\n{text.strip()}")

    md_out = f"# {pdf_path.stem}\n\n" + "\n\n".join(page_parts)
    tables_md = extract_tables_markdown(pdf_path)
    if tables_md:
        md_out += "\n\n" + tables_md

    return md_out


###############################################################################
#                           TABLE EXTRACTION FLOW                             #
###############################################################################

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
                pix = page.get_pixmap(dpi=_RENDER_DPI, alpha=False)
                img = Image.open(io.BytesIO(pix.tobytes("png")))

                if not has_visual_table(img):
                    logger.debug(f"[Page {page_num}] No table structure detected — skipping")
                    continue

                logger.info(f"[Page {page_num}] Table detected visually")

                if ocr_adapter.needs_ocr(page):
                    logger.info(f"[Page {page_num}] Página escaneada — usando OCR para tablas")
                    try:
                        from adapters.ocr_adapter import detect_table_regions, ocr_table_to_markdown
                        table_regions = detect_table_regions(img)
                        if table_regions:
                            md_parts.append(f"## Tables (OCR fallback · page {page_num})\n")
                            for idx, region in enumerate(table_regions, start=1):
                                table_img = img.crop(region)
                                md = ocr_table_to_markdown(table_img)
                                if md.strip():
                                    md_parts.append(f"### Table {idx}\n\n{md}\n")
                    except Exception as exc:
                        logger.warning(f"[Page {page_num}] OCR fallback error → {exc}")
                    continue

                logger.info(f"[Page {page_num}] Página digital — usando Camelot")
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
                except Exception as exc:
                    logger.warning(f"[Page {page_num}] Camelot error → {exc}")

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
                except Exception as exc:
                    logger.warning(f"[Page {page_num}] pdfplumber error → {exc}")

    except Exception as exc:
        logger.error(f"Table extraction failed for {pdf_path} → {exc}")

    return "\n".join(md_parts)


def has_visual_table(img: Image.Image) -> bool:
    """
    Simple heuristic to detect table structures using line detection.

    Args:
        img (PIL.Image): Page image.

    Returns:
        bool: True if visual table structure is detected.
    """
    import numpy as np
    import cv2

    gray = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))

    detected_horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)
    detected_vertical = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)

    table_mask = cv2.add(detected_horizontal, detected_vertical)
    contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return len(contours) > 0