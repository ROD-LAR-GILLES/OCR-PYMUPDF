"""
Configuración centralizada de logging.
"""
import logging
import time
from functools import wraps
from config.ocr_settings import OCRSettings

def setup_logging():
    logging.basicConfig(
        format=OCRSettings.LOG_FORMAT,
        level=getattr(logging, OCRSettings.LOG_LEVEL)
    )

def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        logging.info(f"{func.__name__} executed in {elapsed_time:.2f} seconds")
        return result
    return wrapper
