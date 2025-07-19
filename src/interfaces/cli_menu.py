"""CLI del sistema OCR-PYMUPDF.

Funcionalidades:
1. Listar PDFs
2. Convertir a Markdown
3. Cambiar modo LLM
4. Salir
"""

import sys
from pathlib import Path
from loguru import logger
from domain.use_cases import convert_pdf_to_md
import config.state as state

# ───────────────────────── Helpers ──────────────────────────
def _choose_llm_mode(header: str = "Modo LLM para esta conversión:") -> None:
    """Pregunta el modo LLM y actualiza ``state.LLM_MODE``."""
    print(f"\n{header}")
    print(f"1. Mantener actual ({state.LLM_MODE})")
    print("2. Desactivado")
    print("3. Prompt directo")
    opt = input("Opción (1-3): ").strip()
    if opt == "2":
        state.LLM_MODE = "off"
    elif opt == "3":
        state.LLM_MODE = "prompt"
    # con 1 (o entrada inválida) se mantiene el valor

# ───────────────────────── Constantes ───────────────────────
PDF_DIR = Path("pdfs")

# ───────────────────────── Utilidades ───────────────────────
def listar_pdfs() -> list[str]:
    return [p.name for p in sorted(PDF_DIR.glob("*.pdf"))]

def seleccionar_pdf() -> str | None:
    archivos = listar_pdfs()
    if not archivos:
        print("[INFO] No hay PDF en ./pdfs.")
        return None
    print("Selecciona un PDF:")
    for i, nombre in enumerate(archivos, 1):
        print(f"{i}. {nombre}")
    sel = input("Número: ").strip()
    if sel.isdigit() and 1 <= int(sel) <= len(archivos):
        return archivos[int(sel) - 1]
    print("[ERROR] Selección inválida.")
    return None

def procesar_pdf(pdf_name: str) -> None:
    pdf_path = PDF_DIR / pdf_name
    logger.info(f"Procesando a Markdown: {pdf_path}")
    try:
        md_path = convert_pdf_to_md(pdf_path)
        print(f"[OK] Markdown generado: {md_path}")
    except Exception as exc:
        logger.exception(exc)
        print("[ERROR] Falló la conversión a Markdown.")

# ───────────────────────── Menú principal ───────────────────
def mostrar_menu() -> None:
    """
    Muestra menú principal interactivo.
    """
    while True:
        print("\nOpciones disponibles:")
        print("1. Listar PDFs")
        print("2. Convertir PDF a Markdown")
        print(f"3. Cambiar modo LLM global (actual: {state.LLM_MODE})")
        print("4. Salir")
        
        opcion = input("Seleccione opción (1-4): ").strip()

        # 1) Listar
        if opcion == "1":
            archivos = listar_pdfs()
            if archivos:
                print("\nPDFs encontrados:")
                for n in archivos:
                    print(" -", n)
            else:
                print("[INFO] No se encontraron PDF en ./pdfs.")

        # 2) Markdown
        elif opcion == "2":
            sel = seleccionar_pdf()
            if sel:
                _choose_llm_mode()          # solo para esta conversión
                procesar_pdf(sel)

        # 3) Cambiar modo global
        elif opcion == "3":
            _choose_llm_mode("Selecciona modo LLM global:")

        # 4) Salir
        elif opcion == "4":
            print("Hasta luego.")
            sys.exit(0)

        else:
            print("[ERROR] Opción no reconocida.")