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
# Ejecutar el sistema completo (API y Frontend)
docker compose up -d --build

# Acceder a la interfaz web: http://localhost:8080
# Acceder a la API REST: http://localhost:8000
# Acceder a la documentación API: http://localhost:8000/docs
```

Para más detalles sobre la ejecución con Docker, consulte el archivo [DOCKER_README.md](DOCKER_README.md).

Los contenedores Docker incluyen:
- Todas las dependencias preinstaladas
- Tesseract OCR configurado
- Soporte multilenguaje
- Frontend React con interfaz de usuario moderna
- API REST para integración con otros sistemas
- Volúmenes persistentes para datos

## Uso

### Mediante código
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

### Mediante interfaz web

El proyecto incluye una interfaz web para facilitar el uso sin necesidad de programación.

Para ejecutar la interfaz web, utilice Docker Compose como se describe en la sección de instalación:

```bash
docker compose up -d --build
```

La interfaz web estará disponible en `http://localhost:8080` y permite:
- Subir documentos PDF
- Configurar opciones de procesamiento (OCR, detección de tablas, extracción de imágenes)
- Visualizar resultados en formato Markdown
- Gestionar documentos procesados
- Descargar resultados

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
- `interfaces`: CLI, web y otros puntos de entrada
  - `cli`: Interfaz de línea de comandos
  - `web`: Interfaz web con React y FastAPI
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
