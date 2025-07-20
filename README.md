# OCR-PYMUPDF

## Descripción
Sistema de OCR y procesamiento de documentos PDF basado en arquitectura hexagonal. Integra PyMuPDF para el manejo de PDFs, OCR para documentos escaneados, y refinamiento mediante LLMs para mejorar la calidad del texto extraído.

## Características
- Procesamiento de PDFs digitales y escaneados
- Extracción de texto mediante OCR
- Detección y extracción de tablas
- Refinamiento de texto mediante LLMs
- Exportación a formato Markdown
- Arquitectura hexagonal para mejor mantenibilidad
- Caché de resultados OCR
- Procesamiento paralelo para mejor rendimiento

## Instalación

### Usando Python Virtual Environment
```bash
# Clonar el repositorio
git clone https://github.com/ROD-LAR-GILLES/OCR-PYMUPDF.git
cd OCR-PYMUPDF

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Usando Docker
```bash
# Construir la imagen
docker build -t ocr-pymupdf .

# Ejecutar el contenedor
docker run -v $(pwd)/pdfs:/app/pdfs -v $(pwd)/resultado:/app/resultado ocr-pymupdf

# Usando docker-compose
docker-compose up --build
```

El contenedor Docker incluye:
- Todas las dependencias preinstaladas
- Tesseract OCR configurado
- Soporte multilenguaje
- Volúmenes para pdfs y resultados

## Uso
```python
from src.domain.use_cases.pdf_to_markdown import PDFToMarkdownUseCase
from src.adapters.pymupdf_adapter import PyMuPDFAdapter
from src.adapters.ocr_adapter import OCRAdapter

# Inicializar adaptadores
pdf_adapter = PyMuPDFAdapter()
ocr_adapter = OCRAdapter()

# Crear caso de uso
use_case = PDFToMarkdownUseCase(pdf_adapter, ocr_adapter)

# Procesar documento
result = use_case.execute("documento.pdf")
```

## Configuración
El proyecto utiliza archivos `.env` para la configuración. Variables principales:
- `OCR_LANGUAGE`: Idioma para OCR (default: "spa")
- `OCR_DPI`: DPI para procesamiento de imágenes (default: 300)
- `ENABLE_LLM`: Activar refinamiento con LLM (true/false)
- `CACHE_ENABLED`: Activar caché de OCR (true/false)

## Arquitectura
El proyecto sigue una arquitectura hexagonal (ports & adapters):
- `domain`: Lógica de negocio y entidades
- `adapters`: Implementaciones de puertos
- `infrastructure`: Servicios técnicos
- `interfaces`: CLI y puntos de entrada
- `config`: Configuración del sistema

## API
### Casos de Uso Principales
- `PDFToMarkdownUseCase`: Convierte PDFs a Markdown
- `TableExtractionUseCase`: Extrae tablas de documentos
- `TextRefinementUseCase`: Refina texto mediante LLMs

### Puertos
- `OCRPort`: Interfaz para servicios OCR
- `PDFPort`: Interfaz para manejo de PDFs
- `StoragePort`: Interfaz para almacenamiento
- `LLMPort`: Interfaz para servicios LLM

## Contribuciones
1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nombre`)
3. Commit cambios (`git commit -am 'Añadir característica'`)
4. Push a la rama (`git push origin feature/nombre`)
5. Crear Pull Request

## Licencia
MIT License - Ver archivo `LICENSE` para más detalles.

## Créditos
- PyMuPDF
- Tesseract OCR
- OpenAI GPT
- Camelot-py
- NLTK/spaCy
