# Domain Module

## Descripción
Módulo central que contiene la lógica de negocio, entidades, objetos de valor y puertos de la aplicación.

## Estructura
```
domain/
├── entities/
│   ├── document.py
│   └── __init__.py
├── dtos/
│   ├── content_dtos.py
│   ├── coordinates_dto.py
│   ├── document_dtos.py
│   ├── llm_dtos.py
│   ├── ocr_dtos.py
│   └── __init__.py
├── value_objects/
│   ├── document_metadata.py
│   ├── page.py
│   ├── table.py
│   ├── text_block.py
│   ├── text_coordinates.py
│   └── __init__.py
├── ports/
│   ├── llm_port.py
│   ├── ocr_port.py
│   ├── pdf_port.py
│   ├── storage_port.py
│   └── __init__.py
├── use_cases/
│   ├── pdf_to_markdown.py
│   └── __init__.py
└── exceptions.py
```

## Componentes

### Entidades (entities/)
- `Document`: Entidad principal que representa un documento PDF
  - Atributos: id, path, pages, metadata
  - Métodos: add_page, mark_as_processed, set_error

### DTOs (dtos/)
Objetos de transferencia de datos entre capas:
- `DocumentDTOs`: Input/Output para documentos
- `ContentDTOs`: Contenido de páginas y bloques
- `CoordinatesDTO`: Posicionamiento de elementos
- `OCRDTOs`: Configuración y resultados OCR
- `LLMDTOs`: Configuración y resultados LLM

### Objetos de Valor (value_objects/)
- `Page`: Representa una página del documento
- `TextBlock`: Bloque de texto con posición
- `Table`: Tabla detectada en documento
- `TextCoordinates`: Coordenadas de elementos
- `DocumentMetadata`: Metadatos del documento

### Puertos (ports/)
Interfaces para servicios externos:
- `OCRPort`: Servicio de reconocimiento óptico
- `PDFPort`: Manipulación de PDFs
- `StoragePort`: Almacenamiento de resultados
- `LLMPort`: Servicios de lenguaje natural

### Casos de Uso (use_cases/)
- `PDFToMarkdownUseCase`: Convierte PDF a Markdown
  - Método principal: execute(pdf_path: str) -> str
  - Coordina OCR, extracción y refinamiento

### Excepciones (exceptions.py)
Excepciones específicas del dominio:
- `DocumentError`: Errores de procesamiento
- `OCRError`: Errores en reconocimiento
- `StorageError`: Errores de almacenamiento
- `ValidationError`: Errores de validación

## Uso
```python
from domain.use_cases.pdf_to_markdown import PDFToMarkdownUseCase
from domain.entities.document import Document
from domain.value_objects.page import Page

# Crear caso de uso
use_case = PDFToMarkdownUseCase(pdf_port, ocr_port)

# Ejecutar caso de uso
result = use_case.execute("documento.pdf")
```

## Principios de Diseño
- Entidades inmutables cuando es posible
- Value Objects para conceptos del dominio
- DTOs para transferencia entre capas
- Puertos explícitos para dependencias
- Casos de uso únicos y focalizados

## Validación
- Validación de entrada en DTOs
- Invariantes en entidades
- Verificación de estado en Value Objects
- Control de errores mediante excepciones

## Notas de Implementación
- Uso de dataclasses para inmutabilidad
- Type hints para seguridad de tipos
- Documentación completa de interfaces
- Tests unitarios por componente
