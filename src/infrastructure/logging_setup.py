"""
Configuración centralizada de logging.

Este módulo proporciona una configuración unificada para los logs de la aplicación,
incluyendo handlers para consola y archivos con diferentes niveles de detalle.
"""
import logging
import logging.handlers
import sys
import time
import traceback
import json
import socket
import os
from functools import wraps
from pathlib import Path
from datetime import datetime
from config.ocr_settings import OCRSettings

# Asegurar que existe el directorio de logs
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Subdirectorios para diferentes tipos de logs
error_logs_dir = logs_dir / "errors"
error_logs_dir.mkdir(exist_ok=True)

process_logs_dir = logs_dir / "processing"
process_logs_dir.mkdir(exist_ok=True)

api_logs_dir = logs_dir / "api"
api_logs_dir.mkdir(exist_ok=True)

# Configuración global del logger
logging.basicConfig(
    format=OCRSettings.LOG_FORMAT,
    level=getattr(logging, OCRSettings.LOG_LEVEL)
)

# Logger principal de la aplicación
logger = logging.getLogger("OCR-PYMUPDF")
logger.setLevel(logging.DEBUG)  # Configurar para capturar todos los niveles

# Handler para la consola con formato colorido
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)

# Handler para errores
error_handler = logging.handlers.RotatingFileHandler(
    "logs/errors/ocr_errors.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
error_handler.setLevel(logging.ERROR)
error_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
error_handler.setFormatter(error_format)
logger.addHandler(error_handler)

# Handler para logs detallados
detailed_handler = logging.handlers.RotatingFileHandler(
    "logs/processing/ocr_detailed.log",
    maxBytes=20*1024*1024,  # 20MB
    backupCount=10
)
detailed_handler.setLevel(logging.DEBUG)
detailed_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
detailed_handler.setFormatter(detailed_format)
logger.addHandler(detailed_handler)

# Handler para logs de API
api_handler = logging.handlers.TimedRotatingFileHandler(
    "logs/api/api_access.log",
    when='midnight',
    interval=1,
    backupCount=30
)
api_handler.setLevel(logging.INFO)
api_format = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
api_handler.setFormatter(api_format)
logger.addHandler(api_handler)

# Handler para logs JSON (para análisis estructurado)
json_handler = logging.handlers.RotatingFileHandler(
    "logs/processing/ocr_structured.json",
    maxBytes=20*1024*1024,  # 20MB
    backupCount=5
)
json_handler.setLevel(logging.INFO)

class JsonFormatter(logging.Formatter):
    """Formateador para logs en formato JSON."""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "path": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
            "process": record.process,
            "thread": record.thread,
            "hostname": socket.gethostname()
        }
        
        # Añadir excepción si existe
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
            
        # Añadir datos extra si existen
        if hasattr(record, "data"):
            log_data["data"] = record.data
            
        return json.dumps(log_data)

def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {elapsed_time:.2f} seconds")
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {elapsed_time:.2f} seconds with error: {str(e)}")
            logger.error(f"Arguments: {args}, {kwargs}")
            logger.error(traceback.format_exc())
            raise
    return wrapper

def log_error_details(e, context=""):
    """
    Registra detalles completos de un error.
    
    Args:
        e: La excepción capturada
        context: Información contextual adicional
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    
    # Crear un ID único para el error basado en timestamp
    error_id = f"ERR-{int(time.time())}"
    
    # Registrar en el log de errores
    logger.error(f"===== ERROR DETALLADO {error_id} {'=' * 20}")
    logger.error(f"Contexto: {context}")
    logger.error(f"Excepción: {e.__class__.__name__}: {str(e)}")
    
    # Guardar traza completa
    for line in tb_lines:
        logger.error(line.rstrip())
    
    # Guardar información del sistema
    logger.error(f"Sistema: {sys.platform}")
    logger.error(f"Python: {sys.version}")
    logger.error("=" * 50)
    
    # Guardar un archivo específico para este error
    try:
        error_file = logs_dir / "errors" / f"{error_id}.log"
        with open(error_file, "w") as f:
            f.write(f"Error ID: {error_id}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Contexto: {context}\n")
            f.write(f"Excepción: {e.__class__.__name__}: {str(e)}\n\n")
            f.write("Traceback:\n")
            for line in tb_lines:
                f.write(line)
            f.write("\nInformación del sistema:\n")
            f.write(f"Sistema: {sys.platform}\n")
            f.write(f"Python: {sys.version}\n")
    except Exception as write_error:
        logger.error(f"No se pudo escribir el archivo de error detallado: {write_error}")
    
    return error_id

# Configurar el formateador JSON
json_handler.setFormatter(JsonFormatter())
logger.addHandler(json_handler)

def log_api_request(method, path, params=None, data=None, client_ip=None, status_code=None, response_time=None):
    """
    Registra información sobre una solicitud a la API.
    
    Args:
        method: Método HTTP (GET, POST, etc.)
        path: Ruta de la solicitud
        params: Parámetros de consulta
        data: Datos del cuerpo de la solicitud
        client_ip: IP del cliente
        status_code: Código de estado HTTP
        response_time: Tiempo de respuesta en segundos
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "method": method,
        "path": path,
        "client_ip": client_ip,
        "status_code": status_code,
        "response_time": response_time
    }
    
    if params:
        log_entry["params"] = params
    
    if data and isinstance(data, dict):
        # Omitir datos sensibles si los hay
        if "password" in data:
            data = data.copy()
            data["password"] = "[REDACTED]"
        log_entry["data"] = data
    
    # Usar un logger específico para API
    api_logger = logging.getLogger("OCR-PYMUPDF.api")
    
    # Determinar el nivel de log basado en el código de estado
    if status_code and status_code >= 500:
        api_logger.error(json.dumps(log_entry))
    elif status_code and status_code >= 400:
        api_logger.warning(json.dumps(log_entry))
    else:
        api_logger.info(json.dumps(log_entry))

def log_document_processing(doc_id, filename, status, progress=None, error=None, metadata=None):
    """
    Registra información sobre el procesamiento de un documento.
    
    Args:
        doc_id: ID único del documento
        filename: Nombre del archivo
        status: Estado del procesamiento (processing, completed, error)
        progress: Progreso del procesamiento (0-100)
        error: Mensaje de error si lo hay
        metadata: Metadatos adicionales del documento
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "doc_id": doc_id,
        "filename": filename,
        "status": status
    }
    
    if progress is not None:
        log_entry["progress"] = progress
    
    if error:
        log_entry["error"] = error
    
    if metadata:
        log_entry["metadata"] = metadata
    
    # Usar un logger específico para procesamiento de documentos
    doc_logger = logging.getLogger("OCR-PYMUPDF.documents")
    
    # Determinar el nivel de log basado en el estado
    if status == "error":
        doc_logger.error(json.dumps(log_entry))
    elif status == "completed":
        doc_logger.info(json.dumps(log_entry))
    else:
        doc_logger.debug(json.dumps(log_entry))
    
    # Guardar un archivo de log específico para este documento
    try:
        doc_log_file = logs_dir / "processing" / f"doc_{doc_id}.log"
        
        # Añadir al archivo existente o crear uno nuevo
        mode = "a" if doc_log_file.exists() else "w"
        
        with open(doc_log_file, mode) as f:
            f.write(f"[{datetime.now().isoformat()}] {status.upper()}: {json.dumps(log_entry)}\n")
    except Exception as write_error:
        logger.error(f"No se pudo escribir el archivo de log del documento: {write_error}")
