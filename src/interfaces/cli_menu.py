"""Interfaz de línea de comandos (CLI) para el sistema OCR-PYMUPDF.

Permite listar archivos PDF, seleccionar y convertir a Markdown,
y cambiar el modelo LLM de refinamiento."""

import sys
from pathlib import Path
from loguru import logger
from domain.use_cases import convert_pdf_to_md

import config.state as state
PDF_DIR = Path("pdfs")

def listar_pdfs() -> list[str]:
    """Devuelve la lista de archivos PDF en el directorio de entrada."""
    return [a.name for a in sorted(PDF_DIR.glob("*.pdf"))]

def seleccionar_pdf() -> str | None:
    """Solicita al usuario seleccionar un archivo PDF de la lista por consola."""
    archivos = listar_pdfs()
    if not archivos:
        print("[INFO] No se encontraron PDF en ./pdfs. Copia alguno y vuelve a ejecutar.")
        return None
    print("Selecciona un PDF para convertir a Markdown:")
    for i, archivo in enumerate(archivos, start=1):
        print(f"{i}. {archivo}")
    seleccion = input("Ingresa el número del archivo: ")
    if seleccion.isdigit():
        idx = int(seleccion) - 1
        if 0 <= idx < len(archivos):
            return archivos[idx]
    print("[ERROR] Selección inválida.")
    return None

def procesar_pdf(pdf_name: str) -> None:
    """Procesa el PDF especificado y muestra la ruta del Markdown generado."""
    pdf_path = PDF_DIR / pdf_name
    logger.info(f"Procesando archivo: {pdf_path}")
    try:
        md_path = convert_pdf_to_md(pdf_path)
        print(f"[OK] Markdown generado: {md_path}")
        logger.info(f"Markdown generado: {md_path}")
    except Exception as e:
        logger.exception(f"Error al procesar {pdf_name}: {e}")
        print("[ERROR] Ocurrió un problema al convertir el PDF.")

def mostrar_menu() -> None:
    """Muestra el menú principal interactivo y gestiona la interacción con el usuario."""
    global LLM_MODE
    while True:
        print("\n¿Qué deseas hacer?")
        print("1. Listar PDFs disponibles")
        print("2. Convertir un PDF a Markdown")
        print("3. Cambiar modelo LLM de refinamiento (actual: {})".format(LLM_MODE))
        print("4. Salir")

        opcion = input("Selecciona una opción (1-4): ").strip()

        if opcion == "1":
            archivos = listar_pdfs()
            if archivos:
                print("\nPDFs encontrados en ./pdfs:")
                for nombre in archivos:
                    print(f" - {nombre}")
            else:
                print("[INFO] No se encontraron PDF en ./pdfs.")
        elif opcion == "2":
            seleccion = seleccionar_pdf()
            if seleccion:
                procesar_pdf(seleccion)
        elif opcion == "3":
            print("\nSelecciona el modelo LLM:")
            print("1. Desactivado")
            print("2. Fine-tune personalizado (OPENAI_FT_MODEL)")
            print("3. Prompt directo (OPENAI_PROMPT_MODEL)")
            print("4. Auto (usa fine-tune si está configurado, sino prompt)")
            modelo = input("Opción (1-4): ").strip()
            if modelo == "1":
                LLM_MODE = "off"
            elif modelo == "2":
                LLM_MODE = "ft"
            elif modelo == "3":
                LLM_MODE = "prompt"
            elif modelo == "4":
                LLM_MODE = "auto"
            else:
                print("[WARN] Selección inválida. Se mantiene el modelo actual.")
        elif opcion == "4":
            print("Saliendo del programa.")
            sys.exit(0)
        else:
            print("[ERROR] Opción no reconocida.")