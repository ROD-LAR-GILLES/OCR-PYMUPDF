#!/usr/bin/env python3
"""
Script de diagnóstico simplificado para contenedor Docker.

Este script examina un archivo PDF e identifica posibles problemas
sin depender de otros módulos del proyecto.
"""
import sys
import os
import argparse
from pathlib import Path
import traceback
import logging
import tempfile
import platform
import json
import subprocess
from datetime import datetime

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("diagnose_pdf")

def check_file_info(file_path):
    """Obtiene información básica sobre el archivo."""
    result = {
        "path": str(file_path),
        "exists": file_path.exists(),
        "readable": False,
        "size_bytes": 0,
        "size_human": "0 B",
        "last_modified": None,
        "extension": file_path.suffix.lower()
    }
    
    if result["exists"]:
        try:
            # Comprobar si se puede leer
            with open(file_path, 'rb') as f:
                # Leer solo los primeros bytes para verificar acceso
                f.read(10)
                result["readable"] = True
            
            # Obtener estadísticas del archivo
            stats = file_path.stat()
            result["size_bytes"] = stats.st_size
            result["size_human"] = human_readable_size(stats.st_size)
            result["last_modified"] = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            result["permissions"] = oct(stats.st_mode)[-3:]
        except Exception as e:
            logger.error(f"Error al acceder al archivo {file_path}: {e}")
            result["error"] = str(e)
    
    return result

def check_pdf_validity(file_path):
    """Verifica si el archivo es un PDF válido."""
    result = {
        "is_valid": False,
        "error": None,
        "page_count": 0,
        "is_encrypted": False,
        "has_text": False,
        "metadata": {}
    }
    
    try:
        # Intentar importar PyMuPDF
        import fitz
        
        # Abrir el PDF
        with fitz.open(file_path) as doc:
            result["is_valid"] = True
            result["page_count"] = len(doc)
            result["is_encrypted"] = doc.isEncrypted
            
            # Verificar si tiene texto
            if result["page_count"] > 0:
                # Comprobar la primera página
                text = doc[0].get_text()
                result["has_text"] = len(text) > 10
            
            # Obtener metadatos
            result["metadata"] = doc.metadata
            
    except ImportError:
        result["error"] = "PyMuPDF (fitz) no está instalado"
        logger.error(result["error"])
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Error al validar PDF: {e}")
    
    return result

def check_ocr_capability():
    """Verifica la capacidad de OCR."""
    result = {
        "ocr_available": False,
        "error": None,
        "tesseract_version": None,
        "languages": [],
    }
    
    try:
        # Comprobar si tesseract está instalado
        version_output = subprocess.run(
            ["tesseract", "--version"], 
            capture_output=True, 
            text=True
        )
        if version_output.returncode == 0:
            result["tesseract_version"] = version_output.stdout.split("\n")[0]
            result["ocr_available"] = True
            
            # Obtener idiomas disponibles
            langs_output = subprocess.run(
                ["tesseract", "--list-langs"],
                capture_output=True,
                text=True
            )
            if langs_output.returncode == 0:
                # Filtrar líneas vacías y la línea de encabezado
                result["languages"] = [
                    lang.strip() for lang in langs_output.stdout.split("\n") 
                    if lang.strip() and not lang.startswith("List")
                ]
        else:
            result["error"] = "Tesseract no está instalado o no está en el PATH"
    except Exception as e:
        result["error"] = str(e)
    
    return result

def get_libraries_info():
    """Obtiene información sobre las bibliotecas instaladas."""
    libraries = {}
    
    # PyMuPDF
    try:
        import fitz
        libraries["pymupdf"] = fitz.version[0]
    except ImportError:
        libraries["pymupdf"] = "No instalado"
    
    # Pytesseract
    try:
        import pytesseract
        libraries["pytesseract"] = pytesseract.__version__
    except ImportError:
        libraries["pytesseract"] = "No instalado"
    
    # Pillow
    try:
        from PIL import Image, __version__
        libraries["pillow"] = __version__
    except ImportError:
        libraries["pillow"] = "No instalado"
    
    # Numpy
    try:
        import numpy as np
        libraries["numpy"] = np.__version__
    except ImportError:
        libraries["numpy"] = "No instalado"
    
    # OpenCV
    try:
        import cv2
        libraries["opencv"] = cv2.__version__
    except ImportError:
        libraries["opencv"] = "No instalado"
    
    return libraries

def get_system_info():
    """Obtiene información del sistema."""
    info = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": os.cpu_count(),
        "environment": {
            var: os.environ.get(var, "No definido")
            for var in ["PYTHONPATH", "PATH", "TESSDATA_PREFIX"]
        }
    }
    
    # Comprobar espacio en disco
    try:
        import shutil
        disk = shutil.disk_usage("/")
        info["disk"] = {
            "total": human_readable_size(disk.total),
            "free": human_readable_size(disk.free),
            "used_percent": f"{disk.used / disk.total * 100:.1f}%"
        }
    except:
        pass
    
    return info

def human_readable_size(size_bytes):
    """Convierte bytes a formato legible por humanos."""
    if size_bytes == 0:
        return "0 B"
    
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(size_name) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f} {size_name[i]}"

def diagnose_pdf(pdf_path):
    """Realiza un diagnóstico completo del PDF."""
    logger.info(f"Iniciando diagnóstico para {pdf_path}")
    
    result = {
        "file_info": check_file_info(pdf_path),
        "pdf_validity": check_pdf_validity(pdf_path),
        "ocr_capability": check_ocr_capability(),
        "libraries_info": get_libraries_info(),
        "system_info": get_system_info(),
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return result

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
    
    # Ejecutar diagnóstico
    try:
        result = diagnose_pdf(pdf_path)
        
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
            if isinstance(value, dict):
                print(f"  {key}:")
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key}: {sub_value}")
            else:
                print(f"  {key}: {value}")
        
        # Evaluación del diagnóstico
        print("\n=== EVALUACIÓN ===")
        
        # Verificar si hay problemas con el archivo
        if not result['file_access']['exists']:
            print(" El archivo no existe")
        elif not result['file_access']['readable']:
            print(" El archivo no es legible (problema de permisos)")
        elif result['file_access']['size'] == 0:
            print(" El archivo está vacío")
        else:
            print(" El archivo existe y es accesible")
        
        # Verificar si el PDF es válido
        if not result["pdf_validity"].get("is_valid", False):
            print(f" El archivo no es un PDF válido: {result['pdf_validity'].get('error', 'Razón desconocida')}")
        else:
            print(" El archivo es un PDF válido")
            if result["pdf_validity"].get("is_encrypted", False):
                print(" El PDF está encriptado, lo que puede causar problemas")
            if not result["pdf_validity"].get("has_text", True):
                print("ℹ️ El PDF no contiene texto seleccionable, se usará OCR")
        
        # Verificar capacidad de OCR
        if not result["ocr_capability"].get("ocr_available", False):
            print(f" OCR no disponible: {result['ocr_capability'].get('error', 'Error desconocido')}")
        else:
            print(" OCR está disponible")
            print(f"  Versión de Tesseract: {result['ocr_capability'].get('tesseract_version', 'Desconocida')}")
            print(f"  Idiomas disponibles: {', '.join(result['ocr_capability'].get('languages', ['Ninguno']))}")
        
        # Evaluación de bibliotecas
        required_libs = ["pymupdf", "pytesseract", "pillow"]
        missing_libs = [lib for lib in required_libs if result["libraries_info"].get(lib, "No instalado") == "No instalado"]
        
        if missing_libs:
            print(f" Faltan bibliotecas requeridas: {', '.join(missing_libs)}")
        else:
            print(" Todas las bibliotecas requeridas están instaladas")
        
        # Guardar resultados en un archivo JSON
        try:
            output_dir = Path("./logs")
            output_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = output_dir / f"diagnostico_{timestamp}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)
            
            print(f"\nResultados guardados en: {output_file}")
        except Exception as e:
            print(f"Error al guardar resultados: {e}")
        
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
