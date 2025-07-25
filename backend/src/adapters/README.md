# Adapters Module

## Descripción
Este módulo contiene las implementaciones concretas de los puertos definidos en el dominio, siguiendo el patrón de arquitectura hexagonal.

## Estructura
```
adapters/
├── llm_refiner.py
├── ocr_adapter.py
├── parallel_ocr.py
├── pymupdf_adapter.py
├── table_detector.py
└── __init__.py
```

## Componentes

### llm_refiner.py
Implementa el refinamiento de texto mediante Large Language Models.

#### Clases
- `LLMRefiner`: Implementa `LLMPort`
  - `refine_text(text: str) -> str`: Mejora la calidad del texto mediante LLM
  - `batch_refine(texts: List[str]) -> List[str]`: Procesa múltiples textos
  - `validate_result(text: str) -> bool`: Verifica la calidad del refinamiento

### ocr_adapter.py
Adaptador principal para servicios OCR.

#### Clases
- `OCRAdapter`: Implementa `OCRPort`
  - `extract_text(image: bytes) -> str`: Extrae texto de una imagen
  - `get_confidence() -> float`: Obtiene nivel de confianza
  - `detect_language(text: str) -> str`: Detecta el idioma del texto

### parallel_ocr.py
Implementación paralela del procesamiento OCR.

#### Clases
- `ParallelOCR`
  - `process_pages(pages: List[Image]) -> List[str]`: Procesa páginas en paralelo
  - `merge_results(results: List[str]) -> str`: Combina resultados

### pymupdf_adapter.py
Adaptador para PyMuPDF, maneja operaciones PDF.

#### Clases
- `PyMuPDFAdapter`: Implementa `PDFPort`
  - `extract_text(pdf_path: str) -> str`: Extrae texto de PDF
  - `get_page_count(pdf_path: str) -> int`: Obtiene número de páginas
  - `extract_images(pdf_path: str) -> List[bytes]`: Extrae imágenes

### table_detector.py
Detector y extractor de tablas en documentos.

#### Clases
- `TableDetector`
  - `detect_tables(page: Page) -> List[Table]`: Detecta tablas en una página
  - `extract_table_data(table: Table) -> List[List[str]]`: Extrae datos de tabla
  - `validate_table(table: Table) -> bool`: Valida estructura de tabla

## Uso
```python
from adapters.pymupdf_adapter import PyMuPDFAdapter
from adapters.ocr_adapter import OCRAdapter

# Inicializar adaptadores
pdf_adapter = PyMuPDFAdapter()
ocr_adapter = OCRAdapter()

# Extraer texto de PDF
text = pdf_adapter.extract_text("documento.pdf")

# Procesar imagen con OCR
with open("imagen.png", "rb") as f:
    image_data = f.read()
    text = ocr_adapter.extract_text(image_data)
```

## Dependencias
- PyMuPDF
- Tesseract OCR
- OpenAI API
- Camelot-py
- OpenCV

## Notas de Implementación
- Los adaptadores implementan interfaces definidas en domain/ports/
- Uso de patrones Factory para creación de instancias
- Manejo de errores mediante excepciones personalizadas
- Caché de resultados para optimizar rendimiento
