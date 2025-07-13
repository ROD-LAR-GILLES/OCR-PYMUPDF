"""
Interfaz de línea de comandos (CLI) para el sistema OCR-PYMUPDF.

Este módulo permite al usuario listar archivos PDF disponibles en un directorio,
seleccionar uno de ellos y procesarlo para generar un archivo de salida en formato Markdown.
Utiliza casos de uso definidos en la capa de dominio e incorpora registro de eventos mediante logging.
"""

from pathlib import Path
from domain.use_cases import convert_pdf_to_md
from loguru import logger
import sys

PDF_DIR = Path("pdfs")

def listar_pdfs() -> list[str]:
    """
    Obtiene la lista de archivos PDF presentes en el directorio de entrada.

    Returns:
        list[str]: Lista con los nombres de los archivos PDF encontrados.
    """
    return [a.name for a in sorted(PDF_DIR.glob("*.pdf"))]

def seleccionar_pdf() -> str | None:
    """
    Solicita al usuario que seleccione un archivo PDF de una lista mostrada por consola.

    Returns:
        str | None: Nombre del archivo seleccionado o None si la selección es inválida.
    """
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
    """
    Procesa el archivo PDF especificado y muestra por consola la ruta del archivo Markdown generado,
    o un mensaje de error si ocurre una excepción.

    Args:
        pdf_name (str): Nombre del archivo PDF a procesar.
    """
    pdf_path = PDF_DIR / pdf_name
    logger.info(f"Procesando archivo: {pdf_path}")
    try:
        md_path = convert_pdf_to_md(pdf_path)
        print(f"[OK] Markdown generado: {md_path}")
        logger.info(f"Markdown generado exitosamente: {md_path}")
    except Exception as e:
        logger.exception(f"Error al procesar {pdf_name}: {e}")
        print("[ERROR] Hubo un problema al convertir el PDF.")

def mostrar_menu() -> None:
    """
    Muestra el menú principal interactivo y gestiona la interacción con el usuario.
    """
    while True:
        print("\n¿Qué deseas hacer?")
        print("1. Listar PDFs disponibles")
        print("2. Convertir un PDF a Markdown")
        print("3. Salir")

        opcion = input("Selecciona una opción (1-3): ").strip()

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
            print("Saliendo del programa.")
            sys.exit(0)
        
        else:
            print("[ERROR] Opción no reconocida.")