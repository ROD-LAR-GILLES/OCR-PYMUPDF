# Infrastructure Module

## Descripción
Módulo que proporciona implementaciones técnicas y servicios de infraestructura para la aplicación.

## Estructura
```
infrastructure/
├── file_storage.py
├── logging_setup.py
├── ocr_cache.py
└── __init__.py
```

## Componentes

### file_storage.py
Gestión de almacenamiento de archivos.

#### Clases
- `FileStorage`: Implementa `StoragePort`
  - `save_file(content: str, path: str) -> str`: Guarda contenido
  - `read_file(path: str) -> str`: Lee contenido
  - `exists(path: str) -> bool`: Verifica existencia
  - `delete_file(path: str) -> bool`: Elimina archivo

### logging_setup.py
Configuración centralizada de logging.

#### Funciones
- `setup_logging()`: Configura sistema de logs
- `get_logger(name: str)`: Obtiene logger configurado

#### Características
- Rotación de archivos de log
- Niveles configurables
- Formateo personalizado
- Integración con Loguru

### ocr_cache.py
Sistema de caché para resultados OCR.

#### Clases
- `OCRCache`
  - `get(key: str) -> Optional[str]`: Obtiene resultado cacheado
  - `set(key: str, value: str)`: Almacena resultado
  - `invalidate(key: str)`: Invalida entrada
  - `clear()`: Limpia caché

## Uso
```python
from infrastructure.logging_setup import get_logger
from infrastructure.file_storage import FileStorage
from infrastructure.ocr_cache import OCRCache

# Configurar logging
logger = get_logger(__name__)

# Usar almacenamiento
storage = FileStorage()
storage.save_file("contenido", "archivo.txt")

# Usar caché
cache = OCRCache()
result = cache.get("pagina_1")
```

## Configuración
- Variables de entorno para rutas
- Niveles de log configurables
- Tamaño y política de caché
- Directorios de almacenamiento

## Características
- Manejo de errores robusto
- Logging estructurado
- Caché con expiración
- Almacenamiento seguro

## Dependencias
- Loguru
- python-dotenv
- pathlib
- diskcache

## Notas de Implementación
- Patrón Singleton para servicios
- Manejo de recursos del sistema
- Recuperación ante fallos
- Monitoreo de rendimiento
