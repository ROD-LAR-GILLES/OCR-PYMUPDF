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
from typing import List, Tuple
from datetime import datetime
from domain.ports.document_port import DocumentPort
from domain.dtos.document_dtos import DocumentMetadataDTO
from adapters.out.ocr import parallel_ocr
import os
import config.state as state

# ──────── External imports ────────
import camelot
import fitz
import pdfplumber
from PIL import Image
from loguru import logger
from tabulate import tabulate

# ──────── Internal adapters ────────
from adapters.out.ocr.ocr_adapter import needs_ocr, perform_ocr_on_page

# ──────── Configuración ────────
_RENDER_DPI = 300


class PyMuPDFAdapter(DocumentPort):
    """Adapter that implements DocumentPort using PyMuPDF."""

    def extract_pages(self, pdf_path: Path) -> List[str]:
        """
        Extrae el contenido de todas las páginas de un PDF.
        Primero intenta extraer el texto directamente con PyMuPDF,
        y solo usa OCR si es necesario.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            List[str]: Lista de contenido por página
        """
        results: List[str] = []
        
        try:
            logger.info(f"Iniciando extracción de texto del PDF: {pdf_path}")
            # Verificar que el archivo existe
            if not pdf_path.exists():
                logger.error(f"El archivo no existe: {pdf_path}")
                raise FileNotFoundError(f"El archivo no existe: {pdf_path}")
                
            # Verificar que es un archivo PDF válido
            if not str(pdf_path).lower().endswith('.pdf'):
                logger.error(f"El archivo no es un PDF: {pdf_path}")
                raise ValueError(f"El archivo no es un PDF válido: {pdf_path}")
                
            with fitz.open(pdf_path) as doc:
                logger.info(f"PDF abierto correctamente. Número de páginas: {doc.page_count}")
                
                for page_num, page in enumerate(doc, start=1):
                    logger.info(f"Procesando página {page_num}/{doc.page_count}")
                    
                    try:
                        # Intentar extraer texto directamente
                        text = page.get_text()
                        
                        # Si la página necesita OCR
                        if needs_ocr(page):
                            logger.info(f"Página {page_num} requiere OCR")
                            text = perform_ocr_on_page(page)
                        else:
                            logger.info(f"Página {page_num} procesada sin OCR")
                        
                        results.append(text)
                    except Exception as e:
                        logger.error(f"Error al procesar página {page_num}: {e}")
                        from infrastructure.logging_setup import log_error_details
                        log_error_details(e, f"Procesando página {page_num} de {pdf_path}")
                        # Añadir texto de error a la página
                        results.append(f"[ERROR EN PÁGINA {page_num}]: No se pudo extraer el texto correctamente.")
                    
            return results
                    
        except Exception as e:
            logger.error(f"Error al extraer páginas del PDF: {e}")
            from infrastructure.logging_setup import log_error_details
            log_error_details(e, f"Extracción de páginas de {pdf_path}")
            
            # Si falla el proceso normal, intentar con OCR paralelo como respaldo
            logger.info("Intentando extracción con OCR paralelo como respaldo")
            try:
                return parallel_ocr.run_parallel(pdf_path)
            except Exception as ocr_error:
                logger.critical(f"Falló también el OCR paralelo: {ocr_error}")
                log_error_details(ocr_error, f"OCR paralelo en {pdf_path}")
                return ["Error fatal: No se pudo procesar el documento. Consulte los logs para más detalles."]

    def extract_tables(self, pdf_path: Path) -> List[Tuple[int, str]]:
        """
        Extrae todas las tablas encontradas en el PDF.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            List[Tuple[int, str]]: Lista de (número_página, tabla_markdown)
        """
        tables: List[Tuple[int, str]] = []
        
        try:
            with fitz.open(pdf_path) as doc:
                for page_num, page in enumerate(doc, 1):
                    pix = page.get_pixmap(dpi=_RENDER_DPI, alpha=False)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))

                    if not self._has_visual_table(img):
                        continue

                    # Intentar extraer con Camelot primero
                    try:
                        table_results = camelot.read_pdf(str(pdf_path), pages=str(page_num))
                        if table_results.n > 0:
                            for table in table_results:
                                tables.append((page_num, table.df.to_markdown()))
                            continue
                    except Exception:
                        pass

                    # Si Camelot falla, intentar con pdfplumber
                    try:
                        with pdfplumber.open(pdf_path) as pdf_pl:
                            pg = pdf_pl.pages[page_num - 1]
                            tbls = pg.extract_tables()
                            if tbls:
                                for tbl in tbls:
                                    tables.append((page_num, tabulate(tbl, tablefmt='pipe')))
                    except Exception:
                        pass

        except Exception as e:
            logger.error(f"Error extracting tables: {e}")

        return tables

    def extract_markdown(self, pdf_path: Path) -> str:
        """
        Extrae el contenido de un PDF y lo convierte a Markdown.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            str: Contenido en formato Markdown
        """
        try:
            # Procesar el texto por páginas
            pages = self.extract_pages(pdf_path)
            if not pages:
                raise ValueError("No se pudo extraer texto del PDF")
            
            # Convertir a Markdown
            md_out = ""
            for i, text in enumerate(pages, 1):
                # Solo agregar encabezado si hay más de una página
                if len(pages) > 1:
                    md_out += f"\n## Página {i}\n\n"
                    
                md_out += text + "\n\n"
            
            return md_out.strip()
            
        except Exception as e:
            logger.error(f"Error extracting markdown: {e}")
            raise
            
    def extract_metadata(self, pdf_path: Path) -> DocumentMetadataDTO:
        """
        Extrae los metadatos de un documento PDF.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            DocumentMetadataDTO: Metadatos del documento
        """
        try:
            with fitz.open(pdf_path) as doc:
                metadata = doc.metadata
                
                # Convertir fechas si están disponibles
                creation_date = None
                modification_date = None
                
                if metadata.get("creationDate"):
                    try:
                        # PyMuPDF devuelve fechas en formato "D:YYYYMMDDHHmmSS"
                        date_str = metadata.get("creationDate", "")
                        if date_str.startswith("D:"):
                            date_str = date_str[2:]
                            # Extraer componentes de fecha y hora
                            year = int(date_str[0:4])
                            month = int(date_str[4:6])
                            day = int(date_str[6:8])
                            hour = int(date_str[8:10]) if len(date_str) > 8 else 0
                            minute = int(date_str[10:12]) if len(date_str) > 10 else 0
                            second = int(date_str[12:14]) if len(date_str) > 12 else 0
                            creation_date = datetime(year, month, day, hour, minute, second)
                    except (ValueError, IndexError):
                        logger.warning(f"No se pudo parsear la fecha de creación: {metadata.get('creationDate')}")
                
                if metadata.get("modDate"):
                    try:
                        date_str = metadata.get("modDate", "")
                        if date_str.startswith("D:"):
                            date_str = date_str[2:]
                            # Extraer componentes de fecha y hora
                            year = int(date_str[0:4])
                            month = int(date_str[4:6])
                            day = int(date_str[6:8])
                            hour = int(date_str[8:10]) if len(date_str) > 8 else 0
                            minute = int(date_str[10:12]) if len(date_str) > 10 else 0
                            second = int(date_str[12:14]) if len(date_str) > 12 else 0
                            modification_date = datetime(year, month, day, hour, minute, second)
                    except (ValueError, IndexError):
                        logger.warning(f"No se pudo parsear la fecha de modificación: {metadata.get('modDate')}")
                
                return DocumentMetadataDTO(
                    title=metadata.get("title"),
                    author=metadata.get("author"),
                    subject=metadata.get("subject"),
                    creator=metadata.get("creator"),
                    producer=metadata.get("producer"),
                    creation_date=creation_date,
                    modification_date=modification_date,
                    page_count=doc.page_count
                )
                
        except Exception as e:
            logger.error(f"Error al extraer metadatos del PDF: {e}")
            # Devolver un DTO con valores predeterminados en caso de error
            return DocumentMetadataDTO(page_count=0)



###############################################################################
#                           TABLE EXTRACTION FLOW                             #
###############################################################################

    def _extract_tables_markdown(self, pdf_path: Path) -> str:
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
        logger.info("Fase 2/3: Iniciando detección y extracción de tablas")

        try:
            with fitz.open(pdf_path) as doc:
                total_pages = doc.page_count
                tables_found = 0
                
                for page_num, page in enumerate(doc, start=1):
                    logger.info(f"Analizando página {page_num}/{total_pages} para tablas...")
                    pix = page.get_pixmap(dpi=_RENDER_DPI, alpha=False)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))

                    if not self._has_visual_table(img):
                        logger.debug(f"[Page {page_num}] No se detectaron estructuras de tabla")
                        continue

                    logger.info(f"[Page {page_num}] Se detectó estructura de tabla")
                    tables_found += 1

                    if needs_ocr(page):
                        logger.info(f"[Page {page_num}] Página escaneada - OCR de tablas deshabilitado temporalmente")
                        # TODO: Implementar extracción OCR de tablas
                        # try:
                        #     from adapters.ocr_adapter import detect_table_regions, ocr_table_to_markdown
                        #     table_regions = detect_table_regions(img)
                        #     if table_regions:
                        #         logger.info(f"[Page {page_num}] Se detectaron {len(table_regions)} regiones de tabla")
                        #         md_parts.append(f"## Tables (OCR fallback · page {page_num})\n")
                        #         for idx, region in enumerate(table_regions, start=1):
                        #             logger.info(f"[Page {page_num}] Procesando tabla {idx}/{len(table_regions)}")
                        #             table_img = img.crop(region)
                        #             md = ocr_table_to_markdown(table_img)
                        #             if md.strip():
                        #                 md_parts.append(f"### Table {idx}\n\n{md}\n")
                        #                 logger.success(f"[Page {page_num}] Tabla {idx} extraída exitosamente")
                        # except Exception as exc:
                        #     logger.warning(f"[Page {page_num}] OCR fallback error → {exc}")
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


    def _has_visual_table(self, img: Image.Image) -> bool:
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