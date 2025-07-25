# Interfaz Web para OCR-PYMUPDF

Este directorio contiene la implementación de la interfaz web para OCR-PYMUPDF, que permite a los usuarios subir, procesar y gestionar documentos PDF a través de una interfaz gráfica amigable.

## Estructura

```
web/
├── README.md                # Este archivo
├── __init__.py             # Inicializador del paquete
├── api/                    # API para la interfaz web
│   ├── __init__.py         # Inicializador del paquete API
│   ├── app.py              # Aplicación FastAPI principal
│   └── routes/             # Rutas de la API
│       ├── __init__.py     # Inicializador del paquete de rutas
│       ├── pdf_routes.py   # Rutas para gestión de PDFs
│       └── user_routes.py  # Rutas para gestión de usuarios
└── frontend/              # Frontend con React
    ├── index.html          # HTML principal
    ├── package.json        # Dependencias y scripts
    ├── public/             # Archivos públicos
    ├── src/                # Código fuente React
    └── vite.config.js      # Configuración de Vite
```

## Desarrollo

### Requisitos previos

- Node.js (v16 o superior)
- npm (v8 o superior)
- Python 3.8+ con FastAPI y Uvicorn

### Configuración del entorno de desarrollo

1. **Instalar dependencias del backend**

   ```bash
   # Desde la raíz del proyecto
   pip install -r requirements.txt
   ```

2. **Instalar dependencias del frontend**

   ```bash
   # Desde el directorio del frontend
   cd src/interfaces/web/frontend
   npm install
   ```

### Ejecutar en modo desarrollo

1. **Iniciar el servidor API**

   ```bash
   # Desde la raíz del proyecto
   tools/bin/run_api_local.sh
   ```

2. **Iniciar el servidor de desarrollo del frontend**

   ```bash
   # Desde el directorio del frontend
   cd src/interfaces/web/frontend
   npm run dev
   ```

   El frontend estará disponible en `http://localhost:5173` y se comunicará con la API en `http://localhost:8000`.

### Construir para producción

1. **Construir el frontend**

   ```bash
   # Desde la raíz del proyecto
   tools/scripts/build_frontend.sh
   ```

   Esto generará los archivos estáticos en `src/interfaces/web/frontend/dist`.

2. **Iniciar el servidor web integrado**

   ```bash
   # Desde la raíz del proyecto
   tools/bin/run_web_local.sh
   ```

   La aplicación web completa estará disponible en `http://localhost:8080`.

## Características

- Subida y procesamiento de documentos PDF
- Reconocimiento óptico de caracteres (OCR)
- Visualización de resultados en formato Markdown
- Gestión de documentos (listar, ver detalles, descargar, eliminar)
- Configuración de preferencias de usuario

## Tecnologías utilizadas

- **Backend**: FastAPI, Uvicorn, Python
- **Frontend**: React, Material-UI, Vite
- **Procesamiento**: PyMuPDF, Tesseract OCR