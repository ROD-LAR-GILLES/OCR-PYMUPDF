# API Interna de OCR-PYMUPDF

## Arquitectura

El proyecto OCR-PYMUPDF sigue una arquitectura hexagonal (también conocida como arquitectura de puertos y adaptadores), que separa claramente las responsabilidades y facilita la extensibilidad y el mantenimiento del código.

### Componentes Principales

#### 1. Entidades (Domain)

Representan los objetos centrales del dominio de la aplicación:

- `Document`: Representa un documento PDF con sus metadatos y contenido.
- `TextBlock`: Representa un bloque de texto extraído de un documento.
- `Page`: Representa una página de un documento con su contenido.

#### 2. Puertos (Interfaces)

Definen contratos que deben implementar los adaptadores:

- `DocumentPort`: Interfaz para operaciones con documentos PDF.
- `StoragePort`: Interfaz para almacenamiento de archivos.
- `LLMPort`: Interfaz para interacción con modelos de lenguaje.
- `OCRPort`: Interfaz para operaciones de reconocimiento óptico de caracteres.

#### 3. Casos de Uso

Implementan la lógica de negocio de la aplicación:

- `PDFToMarkdownUseCase`: Convierte documentos PDF a formato Markdown.
- `DocumentComparisonUseCase`: Compara dos versiones de un documento PDF.

#### 4. Adaptadores

Implementan los puertos para interactuar con servicios externos:

- `PyMuPDFAdapter`: Implementa `DocumentPort` usando la biblioteca PyMuPDF.
- `FileStorage`: Implementa `StoragePort` para almacenamiento en disco.
- `LLMRefiner`: Implementa `LLMPort` para refinamiento de texto con modelos de lenguaje.

#### 5. Infraestructura

Proporciona servicios técnicos para la aplicación:

- `OCRCache`: Sistema de caché para resultados de OCR.
- `LLMCache`: Sistema de caché para resultados de modelos de lenguaje.
- `MemoryOptimizer`: Optimizador de memoria para documentos grandes.

## Ejemplos de Uso

### Conversión de PDF a Markdown

```python
from pathlib import Path
from domain.use_cases import PDFToMarkdownUseCase
from adapters.pymupdf_adapter import PyMuPDFAdapter
from infrastructure.file_storage import FileStorage

# Inicializar puertos
document_port = PyMuPDFAdapter()
storage_port = FileStorage()

# Crear caso de uso
use_case = PDFToMarkdownUseCase(
    document_port=document_port,
    storage_port=storage_port
)

# Ejecutar conversión
pdf_path = Path("ruta/al/documento.pdf")
markdown_path = use_case.execute(pdf_path)

print(f"Markdown generado en: {markdown_path}")
```

### Optimización de Memoria para Documentos Grandes

```python
from pathlib import Path
from adapters.memory_optimizer import MemoryOptimizer
from adapters.pymupdf_adapter import PyMuPDFAdapter

# Inicializar optimizador de memoria
optimizer = MemoryOptimizer(batch_size=5)

# Función para procesar una página
def process_page(page):
    # Extraer texto de la página
    text = page.get_text()
    return text

# Procesar documento en lotes
pdf_path = Path("ruta/al/documento_grande.pdf")
results = optimizer.process_document_in_batches(pdf_path, process_page)

print(f"Procesadas {len(results)} páginas con optimización de memoria")
```

### Uso de Caché OCR

```python
from PIL import Image
from infrastructure.ocr_cache import OCRCache

# Inicializar caché OCR
ocr_cache = OCRCache()

# Cargar imagen
image = Image.open("ruta/a/imagen.png")

# Generar hash de la imagen
image_hash = ocr_cache.get_image_hash(image)

# Intentar obtener resultado cacheado
cached_result = ocr_cache.get(image_hash)

if cached_result:
    print("Resultado obtenido de caché")
    text = cached_result
else:
    # Realizar OCR (ejemplo)
    text = perform_ocr(image)
    
    # Guardar en caché
    ocr_cache.set(image_hash, text)
    print("Resultado nuevo guardado en caché")

print(f"Texto extraído: {text[:100]}...")
```

### Comparación de Documentos

```python
from pathlib import Path
from domain.use_cases.document_comparison import DocumentComparisonUseCase
from adapters.pymupdf_adapter import PyMuPDFAdapter
from infrastructure.file_storage import FileStorage

# Inicializar puertos
document_port = PyMuPDFAdapter()
storage_port = FileStorage()

# Crear caso de uso
use_case = DocumentComparisonUseCase(
    document_port=document_port,
    storage_port=storage_port
)

# Ejecutar comparación
original_pdf = Path("ruta/al/documento_original.pdf")
new_pdf = Path("ruta/al/documento_nuevo.pdf")
output_path = Path("ruta/al/informe_comparacion.md")

result = use_case.execute(
    original_pdf_path=original_pdf,
    new_pdf_path=new_pdf,
    output_path=output_path
)

print(f"Informe generado en: {result.report_path}")
print(f"Páginas con diferencias: {len(result.page_differences)}")
```

## Extensibilidad

La arquitectura del proyecto permite extender fácilmente sus capacidades:

1. **Nuevos Adaptadores**: Se pueden implementar nuevos adaptadores para diferentes bibliotecas de procesamiento de PDF, servicios de OCR o modelos de lenguaje.

2. **Nuevos Casos de Uso**: Se pueden añadir nuevos casos de uso que reutilicen los puertos existentes para implementar nuevas funcionalidades.

3. **Optimizaciones**: Los componentes de infraestructura como caché y optimización de memoria pueden ajustarse según las necesidades específicas.