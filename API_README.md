# API REST para OCR-PYMUPDF

Esta API REST permite subir archivos PDF, procesarlos utilizando el motor OCR-PYMUPDF y descargar los resultados en formato Markdown.

## Características

- Subida de archivos PDF
- Procesamiento asíncrono de documentos
- Consulta de estado de procesamiento
- Descarga de resultados en formato Markdown
- Listado de documentos procesados
- Eliminación de documentos

## Requisitos

- Python 3.8+
- FastAPI
- Uvicorn
- Dependencias de OCR-PYMUPDF (ver requirements.txt)

## Configuración

1. Copia el archivo `.env.example` a `.env` y configura las variables de entorno:

```bash
cp .env.example .env
```

2. Edita el archivo `.env` con tus configuraciones:

```
# Configuración de la API
API_HOST=0.0.0.0  # Host donde se ejecutará la API
API_PORT=8000     # Puerto donde se ejecutará la API

# Configuración de LLM (si se usa para refinamiento)
OPENAI_API_KEY=tu_clave_api_aqui
```

## Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt
```

## Ejecución

```bash
# Método 1: Usando el script run_api.py
python tools/bin/run_api.py

# Método 2: Usando uvicorn directamente
uvicorn src.infrastructure.http.api:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoints

### Subir un documento PDF

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

### Obtener estado de un documento

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

### Descargar resultado de un documento

```
GET /api/documents/{doc_id}/download
```

Respuesta: Archivo Markdown con el contenido extraído

### Listar documentos

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

### Eliminar un documento

```
DELETE /api/documents/{doc_id}
```

Respuesta:
```json
{
  "message": "Documento eliminado correctamente"
}
```

## Interfaz de usuario

Puedes acceder a la documentación interactiva de la API en:

```
http://localhost:8000/docs
```

## Estructura de directorios

```
src/
  ├── infrastructure/
  │   └── http/
  │       ├── api.py            # Definición de endpoints
  │       ├── api_server.py     # Configuración del servidor
  │       ├── document_service.py # Servicio para gestión de documentos
  │       └── models.py         # Modelos Pydantic para la API
  └── ...
```