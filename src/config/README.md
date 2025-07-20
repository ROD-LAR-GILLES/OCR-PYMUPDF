# Configuration Module

## Descripción
Módulo que centraliza la configuración del sistema y gestión de variables de entorno.

## Estructura
```
config/
├── ocr_settings.py
├── state.py
└── __init__.py
```

## Componentes

### ocr_settings.py
Configuración para el sistema OCR.

#### Clases
- `OCRSettings`
  - `language: str`: Idioma para OCR
  - `dpi: int`: Resolución de procesamiento
  - `psm: int`: Modo de segmentación de página
  - `oem: int`: Modo de motor OCR
  
#### Funciones
- `load_settings()`: Carga configuración desde .env
- `validate_settings()`: Valida configuración
- `update_settings(settings: Dict)`: Actualiza configuración

### state.py
Gestión del estado global de la aplicación.

#### Clases
- `ApplicationState`
  - `initialized: bool`: Estado de inicialización
  - `processing: bool`: Estado de procesamiento
  - `error: Optional[str]`: Error actual
  
#### Funciones
- `get_state()`: Obtiene estado actual
- `set_state(state: Dict)`: Actualiza estado
- `reset_state()`: Reinicia estado

## Uso
```python
from config.ocr_settings import OCRSettings
from config.state import ApplicationState

# Cargar configuración
settings = OCRSettings()
settings.load_settings()

# Gestionar estado
state = ApplicationState()
state.set_processing(True)
```

## Variables de Entorno
```env
OCR_LANGUAGE=spa
OCR_DPI=300
OCR_PSM=3
OCR_OEM=3
ENABLE_CACHE=true
DEBUG_MODE=false
```

## Características
- Carga automática de configuración
- Validación de valores
- Valores por defecto seguros
- Gestión de estado thread-safe

## Dependencias
- python-dotenv
- pydantic
- typing-extensions

## Notas de Implementación
- Uso de Pydantic para validación
- Patrón Singleton para estado
- Valores inmutables
- Logging de cambios
