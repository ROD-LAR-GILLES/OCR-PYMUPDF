# Clean Architecture - Estructura src/ Reorganizada

##   Estructura Final

```
src/
├── main.py                          # Punto de entrada principal
├── __init__.py
│
├── domain/                          # Capa de Dominio (Entidades y Lógica de Negocio)
│   ├── __init__.py
│   ├── entities/                    # Entidades del dominio
│   │   ├── __init__.py
│   │   ├── document.py
│   │   └── ocr_result.py
│   ├── value_objects/               # Objetos de valor
│   │   ├── __init__.py
│   │   ├── file_path.py
│   │   └── confidence_score.py
│   ├── ports/                       # Interfaces/Puertos
│   │   ├── __init__.py
│   │   ├── document_port.py
│   │   ├── llm_port.py
│   │   ├── llm_provider.py
│   │   ├── ocr_port.py
│   │   └── storage_port.py
│   ├── exceptions/                  # Excepciones del dominio
│   │   ├── __init__.py
│   │   ├── memory_optimizer_exceptions.py
│   │   ├── ocr_exceptions.py
│   │   └── document_exceptions.py
│   ├── models/                      # Modelos del dominio
│   │   ├── __init__.py
│   │   ├── document_model.py
│   │   └── processing_result.py
│   ├── dtos/                        # Data Transfer Objects
│   │   ├── __init__.py
│   │   ├── ocr_request_dto.py
│   │   └── ocr_response_dto.py
│   ├── mappers/                     # Mappers entre capas
│   │   ├── __init__.py
│   │   ├── document_mapper.py
│   │   └── ocr_mapper.py
│   └── use_cases/                   # Casos de uso del dominio
│       ├── __init__.py
│       └── ocr_processing_use_case.py
│
├── application/                     # Capa de Aplicación (Orquestación)
│   ├── __init__.py
│   └── use_cases/                   # Casos de uso de aplicación
│       ├── __init__.py
│       ├── use_cases.py
│       ├── pdf_processing_use_case.py
│       └── document_conversion_use_case.py
│
├── adapters/                        # Capa de Adaptadores
│   ├── __init__.py
│   ├── inbound/                     # Adaptadores de entrada
│   │   ├── __init__.py
│   │   ├── cli/                     # Interfaz de línea de comandos
│   │   │   ├── __init__.py
│   │   │   ├── cli_menu.py
│   │   │   ├── config_menu.py
│   │   │   └── README.md
│   │   └── http/                    # Interfaz HTTP/API
│   │       ├── __init__.py
│   │       └── api/
│   │           ├── __init__.py
│   │           ├── api_server.py
│   │           └── routes/
│   │               ├── __init__.py
│   │               ├── pdf_routes.py
│   │               ├── ocr_routes.py
│   │               └── upload_routes.py
│   └── out/                         # Adaptadores de salida
│       ├── __init__.py
│       ├── llm/                     # Adaptadores LLM
│       │   ├── __init__.py
│       │   ├── llm_refiner.py
│       │   ├── deepseek_api.py
│       │   ├── deepseek_provider.py
│       │   ├── openai_provider.py
│       │   ├── gemini_provider.py
│       │   └── gemini_adapter.py
│       ├── ocr/                     # Adaptadores OCR
│       │   ├── __init__.py
│       │   ├── ocr_adapter.py
│       │   ├── ocr_helper.py
│       │   ├── pymupdf_adapter.py
│       │   ├── parallel_ocr.py
│       │   └── table_detector.py
│       └── storage/                 # Adaptadores de almacenamiento
│           ├── __init__.py
│           ├── file_storage.py
│           └── cache_storage.py
│
├── infrastructure/                  # Capa de Infraestructura
│   ├── __init__.py
│   ├── http/                        # Clientes HTTP
│   │   ├── __init__.py
│   │   ├── aiohttp_client.py
│   │   ├── requests_client.py
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── cors_middleware.py
│   │       └── auth_middleware.py
│   ├── logging_setup.py
│   └── ocr_cache.py
│
└── config/                          # Configuraciones
    ├── __init__.py
    ├── settings.py
    ├── api_settings.py
    ├── llm_config.py
    ├── llm_keys_check.py
    ├── ocr_settings.py
    ├── state.py
    └── language_detection.py
```

##   Limpieza Realizada
###   Archivos Duplicados Eliminados:
- `adapters/parallel_ocr.py` → Mantenido en `adapters/out/ocr/`
- `infrastructure/file_storage.py` → Mantenido en `adapters/out/storage/`
- `adapters/inbound/http/api_server.py` → Movido a ubicación correcta
- `infrastructure/llm_keys_check.py` → Mantenido en `config/`

###   Directorios Vacíos Eliminados:
- `adapters/llm/` → Consolidado en `adapters/out/llm/`
- `adapters/providers/` → Consolidado en `adapters/out/llm/`
- `interfaces/` → Movido a `adapters/inbound/`

###   Archivos Vacíos Eliminados:
- Todos los archivos `.py` sin contenido fueron eliminados
- Se crearon archivos `__init__.py` apropiados donde era necesario

###   Enlaces Simbólicos:
- No se encontraron enlaces simbólicos rotos en la estructura

##   Principios de Clean Architecture Aplicados

### 1. **Capa de Dominio** (`domain/`)
- **Entidades**: Objetos fundamentales del negocio
- **Value Objects**: Objetos inmutables que representan valores
- **Ports**: Interfaces que definen contratos
- **Use Cases**: Lógica de negocio pura
- **Excepciones**: Errores específicos del dominio

### 2. **Capa de Aplicación** (`application/`)
- **Use Cases**: Orquestación de la lógica de negocio
- **Servicios**: Coordinación entre diferentes casos de uso

### 3. **Capa de Adaptadores** (`adapters/`)
- **Inbound**: Puntos de entrada (CLI, HTTP, etc.)
- **Outbound**: Conexiones externas (LLM, OCR, Storage)

### 4. **Capa de Infraestructura** (`infrastructure/`)
- **Implementaciones**: Detalles técnicos concretos
- **Frameworks**: Integraciones con librerías externas

### 5. **Configuración** (`config/`)
- **Settings**: Configuraciones de la aplicación
- **Providers**: Configuración de proveedores externos

##   Dependencias

Las dependencias fluyen **hacia adentro**:
- `infrastructure/` → `adapters/` → `application/` → `domain/`
- `config/` puede ser usado por todas las capas
- `domain/` no depende de ninguna otra capa

##   Beneficios de la Nueva Estructura

1. **Separación de Responsabilidades**: Cada capa tiene un propósito específico
2. **Testabilidad**: Fácil testing mediante mocks de interfaces
3. **Mantenibilidad**: Cambios en una capa no afectan otras
4. **Escalabilidad**: Fácil agregar nuevos adaptadores
5. **Independencia de Frameworks**: El dominio no depende de tecnologías específicas
