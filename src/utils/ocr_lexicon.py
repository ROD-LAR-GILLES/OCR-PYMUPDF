"""
OCR Lexicon Utilities

• Maintains the legal dictionary (`data/legal_words.txt`).
• Persists user corrections in `data/corrections.csv`.
• Generates image snippets around OCR tokens for visual review.
• Provides an interactive CLI (`review_tokens`) that lets the user
  accept, correct, or skip each unknown token and records the decision.

This module lives in the *utils* layer of the Clean Architecture so it
can be imported from adapters, domain, or interface code without adding
external dependencies.
"""
import csv
from pathlib import Path
from unidecode import unidecode
from io import BytesIO
import fitz
from PIL import Image
import pytesseract
import os
import platform
import subprocess

SNIPPET_DIR = Path("resultado/snippets")
SNIPPET_DIR.mkdir(parents=True, exist_ok=True)

CORRECTIONS_PATH = Path("data/corrections.csv")
LEGAL_WORDS_PATH = Path("data/legal_words.txt")

def load_dictionary() -> set[str]:
    """Load the custom legal dictionary.

    Returns
    -------
    set[str]
        A lowercase set with all known legal terms. Returns an empty set
        if the dictionary file does not exist yet.
    """
    if not LEGAL_WORDS_PATH.exists():
        return set()
    with open(LEGAL_WORDS_PATH, encoding="utf-8") as f:
        return set(line.strip().lower() for line in f)

def save_correction(original: str, corrected: str) -> None:
    """Append a new (OCR, correct) pair to *data/corrections.csv*.

    Parameters
    ----------
    original : str
        Token as produced by OCR.
    corrected : str
        Token validated or corrected by the user.
    """
    with open(CORRECTIONS_PATH, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([original.strip(), corrected.strip()])

def generate_snippet(token: str, page_num: int, pdf_path: str, dpi: int = 150) -> str | None:
    """Render a page and crop a small PNG around *token* for visual review.

    The function performs a second pass with Tesseract (`image_to_data`) to
    locate the exact bounding box of the token on the rendered page and
    saves a padded crop under *resultado/snippets/*.

    Parameters
    ----------
    token : str
        Word to locate on the page.
    page_num : int
        1-based page number inside *pdf_path*.
    pdf_path : str
        Path to the PDF currently being processed.
    dpi : int, default 150
        Rendering resolution for the page.

    Returns
    -------
    str | None
        Absolute path to the PNG snippet, or *None* if the token could not
        be located.
    """
    try:
        with fitz.open(pdf_path) as doc:
            page = doc[page_num - 1]  # pages=0-based
            pix = page.get_pixmap(dpi=dpi, alpha=False)
            img_pil = Image.open(BytesIO(pix.tobytes("png")))

            data = pytesseract.image_to_data(img_pil, lang="spa",
                                             output_type=pytesseract.Output.DICT)
            token_norm = token.lower()
            for i, txt in enumerate(data["text"]):
                if txt.strip().lower() == token_norm:
                    x, y, w, h = (data["left"][i], data["top"][i],
                                  data["width"][i], data["height"][i])
                    pad = 20
                    crop = img_pil.crop((max(0, x - pad),
                                         max(0, y - pad),
                                         min(img_pil.width, x + w + pad),
                                         min(img_pil.height, y + h + pad)))
                    out_path = SNIPPET_DIR / f"{Path(pdf_path).stem}_p{page_num}_{token_norm[:10]}.png"
                    crop.save(out_path)
                    return str(out_path)
    except Exception:
        pass
    return None


# Helper: open image with default viewer depending on OS
def _open_image(path: str) -> None:
    """Try to open *path* with the default image viewer for the current OS."""
    try:
        if platform.system() == "Darwin":           # macOS
            subprocess.Popen(["open", path])
        elif platform.system() == "Windows":
            os.startfile(path)                      # type: ignore[attr-defined]
        else:                                       # Linux, WSL
            subprocess.Popen(["xdg-open", path])
    except Exception:
        # Silent failure – CLI will still show the path
        pass

def review_tokens(tokens: list[tuple[str, int, str]]) -> None:
    """Interactive review loop for unknown OCR tokens.

    Parameters
    ----------
    tokens : list[tuple[str, int, str]]
        Sequence with (token, page_num, pdf_path) entries.
    """
    conocidas = load_dictionary()
    vistos: set[str] = set()

    for token, page, doc_path in tokens:
        norm = unidecode(token.lower())
        if norm in conocidas or norm in vistos:
            continue
        vistos.add(norm)

        snippet = generate_snippet(token, page, doc_path)
        print(f"\n {Path(doc_path).name} · page {page}")
        if snippet:
            print(f"Preview saved → {snippet}")
            _open_image(snippet)
        else:
            print(" No snippet found (token not located on page)")

        print(f"» OCR token: '{token}'")
        resp = input("[Enter]=Accept / (c)=Correct / (s)=Skip : ").strip().lower()
        if resp == "c":
            nueva = input("Correction: ").strip()
            save_correction(token, nueva)
        elif resp == "":
            save_correction(token, token)
        else:
            print("· Skipped.")