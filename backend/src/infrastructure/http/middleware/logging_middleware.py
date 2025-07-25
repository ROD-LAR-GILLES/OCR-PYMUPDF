"""
Middleware de logging para la API.

Este módulo proporciona un middleware para FastAPI que registra todas las 
peticiones y respuestas, facilitando el diagnóstico de problemas.
"""
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import FastAPI

from infrastructure.logging_setup import log_api_request

class APILoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para registrar todas las peticiones y respuestas a la API.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Registrar tiempo de inicio
        start_time = time.time()
        
        # Preparar información de la petición
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else None
        
        # Obtener parámetros de consulta
        params = dict(request.query_params)
        
        # Procesar la petición
        try:
            # Llamar al siguiente middleware o endpoint
            response = await call_next(request)
            
            # Calcular tiempo de respuesta
            response_time = time.time() - start_time
            
            # Registrar información de la petición completada
            log_api_request(
                method=method,
                path=path,
                params=params,
                client_ip=client_ip,
                status_code=response.status_code,
                response_time=response_time
            )
            
            return response
            
        except Exception as e:
            # Calcular tiempo hasta el error
            error_time = time.time() - start_time
            
            # Registrar petición con error
            log_api_request(
                method=method,
                path=path,
                params=params,
                client_ip=client_ip,
                status_code=500,  # Internal Server Error
                response_time=error_time,
                data={"error": str(e)}
            )
            
            # Re-lanzar la excepción para que sea manejada por FastAPI
            raise

def add_logging_middleware(app: FastAPI):
    """
    Añade el middleware de logging a una aplicación FastAPI.
    
    Args:
        app: Aplicación FastAPI
    """
    app.add_middleware(APILoggingMiddleware)
