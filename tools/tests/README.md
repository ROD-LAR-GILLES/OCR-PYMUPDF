# Tests Module

## Descripción
Módulo de pruebas organizado según la arquitectura hexagonal del proyecto.

## Estructura
```
tests/
├── domain/
│   ├── test_entities.py
│   ├── test_value_objects.py
│   └── test_use_cases.py
├── adapters/
│   ├── test_ocr_adapter.py
│   ├── test_pymupdf_adapter.py
│   └── test_llm_refiner.py
├── infrastructure/
│   ├── test_file_storage.py
│   └── test_ocr_cache.py
├── interfaces/
│   └── test_cli_menu.py
├── fixtures/
│   ├── digital.pdf
│   ├── scanned.pdf
│   └── tables.pdf
└── conftest.py
```

## Componentes

### Tests de Dominio
Pruebas para la lógica de negocio central.

#### test_entities.py
- `test_document_creation`
- `test_document_page_management`
- `test_document_state`

#### test_value_objects.py
- `test_page_properties`
- `test_text_block_validation`
- `test_coordinates_calculations`

#### test_use_cases.py
- `test_pdf_to_markdown_flow`
- `test_error_handling`
- `test_business_rules`

### Tests de Adaptadores
Pruebas para implementaciones de puertos.

#### test_ocr_adapter.py
- `test_text_extraction`
- `test_language_detection`
- `test_confidence_scoring`

#### test_pymupdf_adapter.py
- `test_pdf_loading`
- `test_text_extraction`
- `test_image_handling`

### Tests de Infraestructura
Pruebas para servicios técnicos.

#### test_file_storage.py
- `test_file_operations`
- `test_path_handling`
- `test_error_cases`

#### test_ocr_cache.py
- `test_cache_operations`
- `test_cache_invalidation`
- `test_concurrent_access`

### Tests de Interfaces
Pruebas para interfaces de usuario.

#### test_cli_menu.py
- `test_menu_display`
- `test_input_handling`
- `test_command_execution`

## Fixtures
- `digital.pdf`: PDF digital para pruebas
- `scanned.pdf`: PDF escaneado para pruebas
- `tables.pdf`: PDF con tablas para pruebas

## Configuración
```python
# conftest.py
import pytest

@pytest.fixture
def sample_pdf():
    return "fixtures/digital.pdf"

@pytest.fixture
def mock_ocr():
    return MockOCRService()
```

## Ejecución
```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests por capa
pytest tests/domain/
pytest tests/adapters/
pytest tests/infrastructure/
pytest tests/interfaces/

# Ejecutar con cobertura
pytest --cov=src
```

## Convenciones
- Naming: test_should_when_given
- Arrange-Act-Assert pattern
- Mocks para dependencias externas
- Fixtures compartidos en conftest.py

## Dependencias
- pytest
- pytest-cov
- pytest-mock
- pytest-asyncio

## Notas de Implementación
- Tests aislados y deterministas
- Cobertura mínima del 80%
- Documentación de casos de prueba
- CI/CD integration
