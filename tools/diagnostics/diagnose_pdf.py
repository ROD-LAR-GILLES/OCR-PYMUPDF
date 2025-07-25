#!/usr/bin/env python3
"""
Script para diagnosticar problemas con archivos PDF específicos.

Este script examina un archivo PDF e identifica posibles problemas que
impidan su procesamiento correcto.
"""
import sys
import os
import argparse
from pathlib import Path
import traceback
import logging

# Asegurar que el directorio raíz del proyecto está en el sys.path
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

# Verificar si el directorio logs existe, crearlo si no
logs_dir = project_root / "logs"
logs_dir.mkdir(exist_ok=True)

# Configurar logging básico para el diagnóstico
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / "diagnose.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("diagnose_pdf")

# Importar después de configurar sys.path
try:
    from src.infrastructure.diagnostics import diagnose_pdf_processing
    from src.infrastructure.logging_setup import setup_logger
except ImportError as e:
    logger.error(f"Error al importar módulos: {e}")
    logger.error("Esto puede deberse a que las dependencias no están instaladas")
    logger.error("Verifique que PyMuPDF (fitz), pytesseract, y Pillow estén instalados")
    print(f"Error al importar módulos: {e}")
    print("Verifique que las dependencias estén instaladas. Consulte el archivo requirements.txt")
    sys.exit(1)

def main():
    # Configurar argparse
    parser = argparse.ArgumentParser(description="Diagnostica problemas con archivos PDF")
    parser.add_argument("pdf_path", help="Ruta al archivo PDF a diagnosticar")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mostrar información detallada")
    
    # Parsear argumentos
    args = parser.parse_args()
    pdf_path = Path(args.pdf_path)
    
    # Verificar que el archivo existe
    if not pdf_path.exists():
        print(f"Error: El archivo {pdf_path} no existe")
        return 1
    
    # Configurar nivel de log
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        print(f"Modo detallado activado")
    
    print(f"Diagnosticando archivo: {pdf_path}")
    logger.info(f"Iniciando diagnóstico para {pdf_path}")
    
    # Ejecutar diagnóstico
    try:
        result = diagnose_pdf_processing(pdf_path)
        
        # Mostrar resultados
        print("\n=== RESULTADOS DEL DIAGNÓSTICO ===")
        print(f"\nInformación del archivo:")
        for key, value in result["file_info"].items():
            print(f"  {key}: {value}")
        
        print("\nValidez del PDF:")
        for key, value in result["pdf_validity"].items():
            if key == "metadata" and isinstance(value, dict):
                print(f"  {key}:")
                for meta_key, meta_value in value.items():
                    print(f"    {meta_key}: {meta_value}")
            else:
                print(f"  {key}: {value}")
        
        print("\nCapacidad de OCR:")
        for key, value in result["ocr_capability"].items():
            print(f"  {key}: {value}")
        
        print("\nInformación de bibliotecas:")
        for key, value in result["libraries_info"].items():
            print(f"  {key}: {value}")
        
        print("\nInformación del sistema:")
        for key, value in result["system_info"].items():
            print(f"  {key}: {value}")
        
        # Evaluación del diagnóstico
        print("\n=== EVALUACIÓN ===")
        
        # Verificar si hay problemas con el archivo
        if not result["file_info"]["exists"]:
            print(" ERROR: El archivo no existe")
        elif not result["file_info"]["readable"]:
            print(" ERROR: El archivo no es legible (problema de permisos)")
        elif result["file_info"].get("size_bytes", 0) == 0:
            print(" ERROR: El archivo está vacío")
        else:
            print(" OK: El archivo existe y es accesible")
        
        # Verificar si el PDF es válido
        if not result["pdf_validity"].get("is_valid", False):
            print(f" ERROR: El archivo no es un PDF válido: {result['pdf_validity'].get('error', 'Razón desconocida')}")
        else:
            print(" OK: El archivo es un PDF válido")
            if result["pdf_validity"].get("is_encrypted", False):
                print(" WARNING: El PDF está encriptado, lo que puede causar problemas")
            if not result["pdf_validity"].get("has_text", True):
                print(" El PDF no contiene texto seleccionable, se usará OCR")
        
        # Verificar capacidad de OCR
        if result["ocr_capability"].get("error"):
            print(f" WARNING: OCR disponible pero con errores: {result['ocr_capability']['error']}")
        else:
            print(" OK: OCR está disponible")
            if result["ocr_capability"].get("accuracy", 0) < 50:
                print(f" WARNING: La precisión del OCR es baja: {result['ocr_capability'].get('accuracy', 0):.1f}%")
        
        # Devolver código de éxito
        return 0
    
    except Exception as e:
        # Registrar error detallado
        logger.exception(f"Error en diagnóstico de {pdf_path}")
        
        # Mostrar error al usuario
        print(f"\nError durante el diagnóstico: {e}")
        
        if args.verbose:
            print("\nTraceback:")
            traceback.print_exc()
        
        # Devolver código de error
        return 1

if __name__ == "__main__":
    sys.exit(main())
