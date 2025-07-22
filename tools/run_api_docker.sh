#!/bin/bash

# Script para ejecutar la API REST de OCR-PYMUPDF con Docker Compose

# Verificar si existe el archivo .env
if [ ! -f .env ]; then
    echo "El archivo .env no existe. Creando a partir de .env.example..."
    cp .env.example .env
    echo "Por favor, edita el archivo .env con tus configuraciones antes de continuar."
    exit 1
fi

# Crear directorios necesarios si no existen
mkdir -p uploads results metadata

# Construir y ejecutar con Docker Compose
docker-compose -f docker-compose.api.yml up --build -d

echo "API REST de OCR-PYMUPDF iniciada en http://localhost:8000"
echo "Documentación disponible en http://localhost:8000/docs"