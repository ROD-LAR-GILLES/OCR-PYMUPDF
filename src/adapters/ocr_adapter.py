# ──────────────────────────────────────────────────────────────
#  File: src/adapters/ocr_adapter.py
#  Python 3.11 • sólo fitz, PIL, pytesseract
# ──────────────────────────────────────────────────────────────

"""Propósito: OCR básico por página usando PyMuPDF + pytesseract

• Renderiza páginas como imagen con fitz (300 DPI)
• Extrae texto con Tesseract OCR
• Utilizado como respaldo para PDFs escaneados

Configuración por defecto:
  - DPI: 300
  - --psm 6 : texto uniforme (ideal para líneas)
  - --oem 1 : motor LSTM (neural net)
  - lang='spa' : idioma español, combinable (ej: 'spa+eng')

Idiomas soportados:
  • eng, spa, fra, deu, ita, por, jpn, chi_sim, chi_tra...
  • Listar con: tesseract --list-langs
  • Instalar con: sudo apt install tesseract-ocr-spa (etc.)

Ejemplo de uso:
  image_to_string(img, lang="spa", config="--psm 6 --oem 1")
"""

import logging
from io import BytesIO

import re
import unicodedata

# Terceros
import cv2
import fitz
import numpy as np
import pytesseract
from PIL import Image

# ───────────────────────── Configuración global ─────────────────────────
DPI              = 600
TESSERACT_CONFIG = f"--psm 6 --oem 1 -c user_defined_dpi={DPI}"
OCR_LANG         = "spa"
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

# ───────────────────────── OCR Principal ─────────────────────────


def perform_ocr_on_page(page: fitz.Page) -> str:
    """
    Realiza OCR sobre una página de PDF utilizando Tesseract vía pytesseract.

    Simplifica el preprocesamiento para mejorar estabilidad.
    """
    pix = page.get_pixmap(dpi=DPI, alpha=False)
    img = Image.open(BytesIO(pix.tobytes("png")))

    # Preprocesamiento liviano: escala de grises
    gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    img = Image.fromarray(gray)

    # Configuración fija: PSM 6 (bloques uniformes), idioma español
    config = f"--psm 6 --oem 1 -c user_defined_dpi={DPI}"
    lang = "spa"

    raw = pytesseract.image_to_string(img, lang=lang, config=config)
    # Eliminar guiones de fin de línea que cortan palabras
    raw = re.sub(r"-\n(\w+)", r"\1", raw)
    cleaned = _cleanup_text(raw)
    return detect_structured_headings(cleaned)


# ───────────────────── Post‑OCR cleanup ──────────────────────
def _cleanup_text(text: str) -> str:
    """
    Normaliza y limpia el texto OCR:
    • Normaliza Unicode a NFKC.
    • Elimina caracteres no imprimibles.
    • Convierte múltiples espacios en uno.
    • Retira líneas con muy baja proporción de caracteres alfabéticos (<30 %).

    Args:
        text (str): Texto bruto OCR.

    Returns:
        str: Texto limpio.
    """
    text = unicodedata.normalize("NFKC", text)
    # Normalización Unicode y limpieza de ruido OCR
    # Sustituir cualquier carácter que NO sea letra, número, puntuación básica o espacio
    text = re.sub(r"[^\w\sÁÉÍÓÚÜÑñáéíóúü¿¡.,;:%\-()/]", " ", text)
    # Colapsar espacios repetidos
    text = re.sub(r"\s{2,}", " ", text)

    # Filtrar líneas con mucho ruido
    cleaned_lines = []
    for line in text.splitlines():
        letters = sum(c.isalpha() for c in line)
        ratio = letters / max(len(line), 1)
        if ratio >= 0.3:
            cleaned_lines.append(line.strip())
    return "\n".join(cleaned_lines)

# ──────────────── Visualización de regiones OCR ────────────────

def visualize_ocr_regions(page: fitz.Page, output_path: str = "ocr_regions.png") -> None:
    """
    Dibuja las regiones de texto detectadas por Tesseract en la imagen de una página y guarda el resultado.

    Args:
        page (fitz.Page): Página PDF a procesar.
        output_path (str): Ruta donde guardar la imagen con las cajas dibujadas.
    """


    pix = page.get_pixmap(dpi=DPI, alpha=False)
    img_pil = Image.open(BytesIO(pix.tobytes("png")))
    img = np.array(img_pil)

    # Convertir a RGB si es necesario
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    data = pytesseract.image_to_data(img, lang=OCR_LANG, config=TESSERACT_CONFIG, output_type=pytesseract.Output.DICT)

    n_boxes = len(data['level'])
    for i in range(n_boxes):
        (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Guardar o mostrar la imagen
    Image.fromarray(img).save(output_path)
    logging.info(f"Regiones OCR visualizadas en: {output_path}")

# ─────────────────────── Preprocesamiento ───────────────────────

def correct_rotation(img_pil: Image.Image) -> Image.Image:
    """
    Corrige la rotación de una imagen usando detección automática vía Tesseract OSD.

    Args:
        img_pil (Image.Image): Imagen original.

    Returns:
        Image.Image: Imagen rotada si se detectó desviación de ángulo.
    """
    try:
        osd = pytesseract.image_to_osd(img_pil)
        angle = int([line for line in osd.split('\n') if 'Rotate' in line][0].split(':')[-1])
        if angle != 0:
            return img_pil.rotate(-angle, expand=True)
    except Exception:
        pass  # Si falla, seguimos con la imagen original
    return img_pil

# ───────────── Heurísticas y Detección de Tablas ────────────────


def estimate_psm_for_page(img_pil: Image.Image) -> int:
    """
    Estima automáticamente el valor de PSM (Page Segmentation Mode) para Tesseract
    según las características visuales de la imagen renderizada.

    Heurística:
        - Pocas líneas -> PSM 7 (una sola línea)
        - Muchas columnas visibles -> PSM 4 (flujo de columnas)
        - Distribución moderada -> PSM 6 (bloques uniformes)
        - Muy ruidoso o disperso -> PSM 11 (OCR general)

    Args:
        img_pil (Image.Image): Imagen renderizada de la página.

    Returns:
        int: Valor de PSM sugerido.
    """
    img = np.array(img_pil.convert("L"))
    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(255 - binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    num_boxes = len(contours)

    if num_boxes < 5:
        return 7
    elif num_boxes > 50:
        return 11
    elif 20 < num_boxes <= 50:
        return 4
    else:
        return 6


def has_visual_table(img_pil: Image.Image) -> bool:
    """
    Detecta si una imagen contiene una tabla visualmente, evaluando líneas horizontales/verticales.

    Args:
        img_pil (Image.Image): Imagen de la página.

    Returns:
        bool: True si se detecta estructura tabular, False si no.
    """
    img = np.array(img_pil.convert("L"))
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    # Detección de líneas
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100,
                            minLineLength=50, maxLineGap=10)
    if lines is None:
        return False

    horizontal = 0
    vertical = 0
    for x1, y1, x2, y2 in lines[:, 0]:
        if abs(y2 - y1) < 10:  # Horizontal
            horizontal += 1
        elif abs(x2 - x1) < 10:  # Vertical
            vertical += 1

    return horizontal >= 2 and vertical >= 2

# ─────────────────────── Utilidades OCR ─────────────────────────

def needs_ocr(page: fitz.Page) -> bool:
    """
    Determina si una página necesita OCR revisando si contiene texto seleccionable.

    Args:
        page (fitz.Page): Página a analizar.

    Returns:
        bool: True si no hay texto y se debe aplicar OCR.
    """
    return page.get_text("text").strip() == ""

# ────────────────── Extraer bloques visuales del layout ──────────────────
def extract_blocks(page: fitz.Page) -> list[tuple[float, float, float, float, str]]:
    """
    Extrae bloques de texto con coordenadas de la página.

    Returns:
        Lista de tuplas (x0, y0, x1, y1, texto)
    """
    blocks = page.get_text("blocks")
    return [(b[0], b[1], b[2], b[3], b[4].strip()) for b in blocks if b[4].strip()]

# ────────────── Detección y jerarquización de encabezados legales ──────────────
def detect_structured_headings(text: str) -> str:
    """
    Aplica formato Markdown a encabezados legales típicos como 'VISTOS', 'CONSIDERANDO', 'RESUELVO', 'DECRETO', etc.

    Args:
        text (str): Texto OCR limpio.

    Returns:
        str: Texto con encabezados jerarquizados en Markdown.
    """
    headings = ["VISTOS", "CONSIDERANDO", "RESUELVO", "DECRETO", "FUNDAMENTO", "TENIENDO PRESENTE", "POR TANTO"]
    for heading in headings:
        # Reemplaza solo si aparece como línea sola o seguida de dos puntos
        text = re.sub(rf"(?m)^\s*{heading}[:\s]*", f"\n### {heading}\n", text)
    return text