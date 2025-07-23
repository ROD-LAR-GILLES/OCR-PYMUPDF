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

## Ejecución con Docker

### Requisitos previos

- Docker instalado en su sistema
- Docker Compose instalado en su sistema

### Configuración

1. Asegúrese de tener un archivo `.env` en la raíz del proyecto. Si no existe, cópielo desde `.env.example`:

```bash
cp .env.example .env
```

2. Edite el archivo `.env` para configurar sus claves de API y otras configuraciones según sea necesario.

### Ejecución

Para iniciar todos los servicios (API y Frontend):

```bash
docker compose up -d --build
```

Esto construirá las imágenes si es necesario y ejecutará los contenedores en segundo plano.

### Acceso a los servicios

- **Frontend**: http://localhost:8080
- **API REST**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs

### Detener los servicios

Para detener todos los servicios:

```bash
docker compose down
```

### Visualizar logs

Para ver los logs de todos los servicios:

```bash
docker compose logs -f
```

Para ver los logs de un servicio específico:

```bash
docker compose logs -f ocr-api
```

o

```bash
docker compose logs -f ocr-frontend
```

### Volúmenes persistentes

Los siguientes directorios se montan como volúmenes para persistencia de datos:

- `./pdfs`: Archivos PDF procesados
- `./resultado`: Resultados del procesamiento
- `./uploads`: Archivos subidos temporalmente
- `./metadata`: Metadatos de los documentos
- `./tools/data`: Datos de configuración y modelos

## API REST

Esta API REST permite subir archivos PDF, procesarlos utilizando el motor OCR-PYMUPDF y descargar los resultados en formato Markdown.

### Características

- Subida de archivos PDF
- Procesamiento asíncrono de documentos
- Consulta de estado de procesamiento
- Descarga de resultados en formato Markdown
- Listado de documentos procesados
- Eliminación de documentos

### Endpoints

#### Subir un documento PDF

```
POST /api/documents/
```

Parámetros del formulario:
- `file`: Archivo PDF a procesar
- `use_llm` (opcional): Indica si se debe usar LLM para refinamiento (true/false)
- `extract_tables` (opcional): Indica si se deben extraer tablas (true/false)

Respuesta:
```json
{
  "id": "documento_id",
  "filename": "documento.pdf",
  "status": "processing",
  "created_at": "2023-06-15T10:30:00Z"
}
```

#### Obtener estado de un documento

```
GET /api/documents/{doc_id}/status
```

Respuesta:
```json
{
  "id": "documento_id",
  "filename": "documento.pdf",
  "status": "completed",
  "progress": 100,
  "created_at": "2023-06-15T10:30:00Z",
  "completed_at": "2023-06-15T10:35:00Z"
}
```

#### Descargar resultado de un documento

```
GET /api/documents/{doc_id}/download
```

Respuesta: Archivo Markdown con el contenido extraído

#### Listar documentos

```
GET /api/documents/?skip=0&limit=10
```

Respuesta:
```json
{
  "total": 25,
  "items": [
    {
      "id": "documento_id_1",
      "filename": "documento1.pdf",
      "status": "completed",
      "created_at": "2023-06-15T10:30:00Z"
    },
    {
      "id": "documento_id_2",
      "filename": "documento2.pdf",
      "status": "processing",
      "created_at": "2023-06-15T11:30:00Z"
    }
  ]
}
```

#### Eliminar un documento

```
DELETE /api/documents/{doc_id}
```

Respuesta:
```json
{
  "message": "Documento eliminado correctamente"
}
```

## Arquitectura

El proyecto sigue una arquitectura hexagonal (ports & adapters):

### Domain Module

Módulo central que contiene la lógica de negocio, entidades, objetos de valor y puertos de la aplicación.

#### Estructura
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

### Adapters Module

Este módulo contiene las implementaciones concretas de los puertos definidos en el dominio, siguiendo el patrón de arquitectura hexagonal.

#### Estructura
```
adapters/
├── llm_refiner.py
├── ocr_adapter.py
├── parallel_ocr.py
├── pymupdf_adapter.py
├── table_detector.py
└── __init__.py
```

### Infrastructure Module

Módulo que proporciona implementaciones técnicas y servicios de infraestructura para la aplicación.

#### Estructura
```
infrastructure/
├── file_storage.py
├── logging_setup.py
├── ocr_cache.py
└── __init__.py
```

### Interfaces Module

Módulo que proporciona interfaces de usuario y puntos de entrada para la aplicación.

#### Estructura
```
interfaces/
├── cli_menu.py
└── __init__.py
```

### Configuration Module

Módulo que centraliza la configuración del sistema y gestión de variables de entorno.

#### Estructura
```
config/
├── ocr_settings.py
├── state.py
└── __init__.py
```

## Contribución

Seguimos la convención de [Conventional Commits](https://www.conventionalcommits.org/) para los mensajes de commit:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Cambios de estilo de código (formato, punto y coma, etc.)
- `refactor`: Refactorización de código
- `test`: Añadir o actualizar tests
- `chore`: Tareas de mantenimiento, actualizaciones de dependencias
- `ci`: Cambios relacionados con CI/CD
- `perf`: Mejoras de rendimiento

### Scopes
- `deps`: Dependencias
- `core`: Funcionalidad central
- `ocr`: Cambios relacionados con OCR
- `pdf`: Procesamiento de PDF
- `nlp`: Procesamiento de Lenguaje Natural
- `ml`: Machine Learning
- `ui`: Interfaz de Usuario
- `test`: Relacionado con pruebas

### Ejemplos
```
feat(ocr): añadir nuevo filtro de preprocesamiento de imágenes
fix(pdf): corregir cálculo de rotación de página
chore(deps): actualizar dependencias del proyecto
docs: actualizar instrucciones de instalación
```
