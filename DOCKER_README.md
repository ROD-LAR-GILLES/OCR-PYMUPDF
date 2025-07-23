# Ejecución de OCR-PYMUPDF con Docker

Este documento explica cómo ejecutar el sistema OCR-PYMUPDF utilizando Docker Compose.

## Requisitos previos

- Docker instalado en su sistema
- Docker Compose instalado en su sistema

## Configuración

1. Asegúrese de tener un archivo `.env` en la raíz del proyecto. Si no existe, cópielo desde `.env.example`:

```bash
cp .env.example .env
```

2. Edite el archivo `.env` para configurar sus claves de API y otras configuraciones según sea necesario.

## Ejecución

Para iniciar todos los servicios (API y Frontend):

```bash
docker compose up -d --build
```

Esto construirá las imágenes si es necesario y ejecutará los contenedores en segundo plano.

## Acceso a los servicios

- **Frontend**: http://localhost:8080
- **API REST**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs

## Detener los servicios

Para detener todos los servicios:

```bash
docker compose down
```

## Visualizar logs

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

## Volúmenes persistentes

Los siguientes directorios se montan como volúmenes para persistencia de datos:

- `./pdfs`: Archivos PDF procesados
- `./resultado`: Resultados del procesamiento
- `./uploads`: Archivos subidos temporalmente
- `./metadata`: Metadatos de los documentos
- `./data`: Datos de configuración y modelos

## Reconstruir las imágenes

Si necesita reconstruir las imágenes después de cambios en el código:

```bash
docker compose build
```

O para reconstruir e iniciar en un solo comando:

```bash
docker compose up -d --build
```