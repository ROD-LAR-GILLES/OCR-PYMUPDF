#!/bin/bash
# Script para ejecutar el diagnóstico de PDF dentro del contenedor Docker

# Comprobar si se ha pasado un argumento (ruta al PDF)
if [ -z "$1" ]; then
    echo "Error: Debe especificar la ruta al archivo PDF"
    echo "Uso: $0 ruta/al/archivo.pdf [--verbose]"
    exit 1
fi

PDF_PATH="$1"
VERBOSE=""

# Comprobar si se ha pasado la opción --verbose
if [ "$2" == "--verbose" ]; then
    VERBOSE="--verbose"
fi

# Verificar si el archivo existe
if [ ! -f "$PDF_PATH" ]; then
    echo "Error: El archivo $PDF_PATH no existe"
    exit 1
fi

# Obtener ruta relativa al directorio actual
CURRENT_DIR=$(pwd)
if [[ "$PDF_PATH" = /* ]]; then
    # Es una ruta absoluta
    if [[ "$PDF_PATH" == "$CURRENT_DIR"* ]]; then
        # Convertir a ruta relativa
        REL_PATH="${PDF_PATH#$CURRENT_DIR/}"
    else
        echo "Error: El archivo debe estar dentro del directorio del proyecto"
        exit 1
    fi
else
    # Ya es una ruta relativa
    REL_PATH="$PDF_PATH"
fi

# Obtener directorio y nombre de archivo
DIR_PATH=$(dirname "$REL_PATH")
FILE_NAME=$(basename "$REL_PATH")

echo "Ejecutando diagnóstico del archivo: $FILE_NAME"
echo "Dentro del contenedor en la ruta: /app/$REL_PATH"

# Comprobar si el contenedor está en ejecución
CONTAINER_RUNNING=$(docker ps -q -f name=ocr-pymupdf-api)

if [ -z "$CONTAINER_RUNNING" ]; then
    echo "El contenedor ocr-pymupdf-api no está en ejecución"
    echo "Iniciando el contenedor con docker-compose..."
    
    # Iniciar el contenedor
    docker-compose up -d ocr-api
    
    # Esperar a que el contenedor esté listo
    echo "Esperando a que el contenedor esté listo..."
    sleep 10
fi

# Ejecutar el script de diagnóstico dentro del contenedor
docker exec ocr-pymupdf-api python /app/tools/diagnose_docker.py "/app/$REL_PATH" $VERBOSE

# Mostrar mensaje final
echo ""
echo "Diagnóstico completado."
