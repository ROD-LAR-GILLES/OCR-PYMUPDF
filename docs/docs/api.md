# API Reference

## Introducción

Esta documentación describe la API interna del proyecto OCR-PYMUPDF, detallando los componentes principales, sus interfaces y cómo interactúan entre sí.

## Arquitectura

El proyecto sigue una arquitectura hexagonal (también conocida como Ports & Adapters), que separa claramente:

- **Dominio**: Lógica de negocio central
- **Puertos**: Interfaces abstractas
- **Adaptadores**: Implementaciones concretas
- **Infraestructura**: Servicios técnicos

## Componentes Principales

### Entidades

#### Document

Representa un documento PDF con sus páginas y metadatos.

```python
class Document:
    id: str                      # Identificador único
    path: str                    # Ruta al archivo
    pages: List[Page]            # Lista de páginas
    metadata: DocumentMetadata   # Metadatos
    processed: bool              # Estado de procesamiento
    error: Optional[str]         # Mensaje de error si existe
```

### Puertos

#### DocumentPort

Interfaz para operaciones con documentos PDF.

```python
class DocumentPort(ABC):
    @abstractmethod
    def extract_pages(self, pdf_path: Path) -> List[str]:
        """Extrae el contenido de todas las páginas de un PDF."""
        pass
    
    @abstractmethod
    def extract_tables(self, pdf_path: Path) -> Dict[int, List[str]]:
        """Extrae tablas de un PDF."""
        pass
    
    @abstractmethod
    def extract_metadata(self, pdf_path: Path) -> DocumentMetadata:
        """Extrae metadatos de un PDF."""
        pass
```

#### OCRPort

Interfaz para procesamiento OCR.

```python
class OCRPort(ABC):
    @abstractmethod
    def extract_text(self, image: bytes) -> str:
        """Extrae texto de una imagen usando OCR."""
        pass
    
    @abstractmethod
    def detect_tables(self, image: bytes) -> List[dict]:
        """Detecta tablas en una imagen."""
        pass
    
    @abstractmethod
    def needs_ocr(self, page_content: str) -> bool:
        """Determina si una página necesita OCR."""
        pass
```

#### LLMPort

Interfaz para modelos de lenguaje.

```python
class LLMPort(ABC):
    @abstractmethod
    def refine_text(self, text: str) -> str:
        """Refina texto usando un modelo de lenguaje."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Verifica si el servicio LLM está disponible."""
        pass
```

#### StoragePort

Interfaz para almacenamiento de archivos.

```python
class StoragePort(ABC):
    @abstractmethod
    def save_markdown(self, content: str, output_path: Path) -> Path:
        """Guarda contenido en formato Markdown."""
        pass
```

### Casos de Uso

#### PDFToMarkdownUseCase

Caso de uso principal para convertir PDF a Markdown.

```python
class PDFToMarkdownUseCase:
    def __init__(self, document_port: DocumentPort, storage_port: StoragePort, llm_port: Optional[LLMPort] = None):
        # Inicialización
        
    def execute(self, pdf_path: Path) -> Path:
        """Convierte un archivo PDF en un archivo Markdown."""
        # Implementación
```

## Adaptadores

### PyMuPDFAdapter

Implementación de DocumentPort usando PyMuPDF.

```python
class PyMuPDFAdapter(DocumentPort):
    def extract_pages(self, pdf_path: Path) -> List[str]:
        # Implementación
    
    def extract_tables(self, pdf_path: Path) -> Dict[int, List[str]]:
        # Implementación
    
    def extract_metadata(self, pdf_path: Path) -> DocumentMetadata:
        # Implementación
```

### OCRAdapter

Implementación de OCRPort usando Tesseract.

```python
class OCRAdapter(OCRPort):
    def extract_text(self, image: bytes) -> str:
        # Implementación
    
    def detect_tables(self, image: bytes) -> List[dict]:
        # Implementación
    
    def needs_ocr(self, page_content: str) -> bool:
        # Implementación
```

## Infraestructura

### OCRCache

Sistema de caché para resultados OCR.

```python
class OCRCache:
    def get(self, key: str) -> Optional[str]:
        # Implementación
    
    def set(self, key: str, value: str) -> None:
        # Implementación
    
    def invalidate(self, key: str) -> None:
        # Implementación
    
    def clear(self) -> None:
        # Implementación
```

### LLMCache

Sistema de caché para resultados LLM.

```python
class LLMCache:
    def get(self, text: str, model: str, temperature: float = 0.0) -> Optional[str]:
        # Implementación
    
    def set(self, text: str, model: str, temperature: float, result: str) -> None:
        # Implementación
    
    def invalidate(self, text: str, model: str, temperature: float = 0.0) -> None:
        # Implementación
    
    def clear(self) -> None:
        # Implementación
```

### MemoryOptimizer

Optimizador de memoria para documentos grandes.

```python
class MemoryOptimizer:
    def process_document_in_batches(self, pdf_path: Path, page_processor: Callable) -> List:
        # Implementación
    
    def optimize_image(self, image: Image.Image, max_size: int = 1500) -> Image.Image:
        # Implementación
```

## Ejemplos de Uso

### Convertir PDF a Markdown

```python
from pathlib import Path
from adapters.pymupdf_adapter import PyMuPDFAdapter
from infrastructure.file_storage import FileStorage
from domain.use_cases.pdf_to_markdown import PDFToMarkdownUseCase

# Inicializar puertos
document_port = PyMuPDFAdapter()
storage_port = FileStorage()

# Crear caso de uso
use_case = PDFToMarkdownUseCase(document_port, storage_port)

# Ejecutar
pdf_path = Path("documento.pdf")
markdown_path = use_case.execute(pdf_path)
print(f"Markdown generado en: {markdown_path}")
```

### Usar Optimizador de Memoria

```python
from pathlib import Path
from adapters.memory_optimizer import MemoryOptimizer
from adapters.ocr_adapter import perform_ocr_on_page

# Inicializar optimizador
optimizer = MemoryOptimizer(batch_size=3)

# Procesar documento grande
pdf_path = Path("documento_grande.pdf")
results = optimizer.process_document_in_batches(pdf_path, perform_ocr_on_page)

# Usar resultados
for i, text in enumerate(results):
    print(f"Página {i+1}: {text[:100]}...")
```

### Usar Caché OCR

```python
from PIL import Image
from infrastructure.ocr_cache import OCRCache
from adapters.ocr_adapter import perform_ocr_on_image

# Inicializar caché
cache = OCRCache()

# Cargar imagen
image = Image.open("pagina.png")

# Generar hash
image_hash = cache.get_image_hash(image)

# Verificar caché
result = cache.get(image_hash)
if result is None:
    # No está en caché, procesar
    result = perform_ocr_on_image(image)
    cache.set(image_hash, result)

print(f"Texto OCR: {result[:100]}...")
```