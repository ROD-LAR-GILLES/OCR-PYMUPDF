#!/bin/bash

# Script para ejecutar la API REST de OCR-PYMUPDF localmente

# Verificar si existe el archivo .env
if [ ! -f .env ]; then
    echo "El archivo .env no existe. Creando a partir de .env.example..."
    cp .env.example .env
    echo "Por favor, edita el archivo .env con tus configuraciones antes de continuar."
    exit 1
fi

# Crear directorios necesarios si no existen
mkdir -p uploads results metadata

# Ejecutar la API
python tools/bin/run_api.py