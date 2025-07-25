#!/bin/bash
# Script para probar la ruta POST /api/documents

echo "Realizando prueba de carga de documento..."

# Crear un pequeño archivo PDF de prueba si no existe
TEST_PDF="test_upload.pdf"
if [ ! -f "$TEST_PDF" ]; then
    echo "Creando PDF de prueba..."
    echo "Este es un PDF de prueba" > test.txt
    if command -v convert &> /dev/null; then
        convert test.txt "$TEST_PDF"
    else
        echo "No se pudo crear el PDF de prueba, asegúrate de tener ImageMagick instalado"
        echo "Utilizaremos un PDF existente para la prueba"
        # Buscar un PDF existente en la carpeta pdfs
        TEST_PDF=$(find pdfs -name "*.pdf" | head -n 1)
        if [ -z "$TEST_PDF" ]; then
            echo "No se encontró ningún PDF para realizar la prueba"
            exit 1
        fi
    fi
fi

echo "Usando archivo: $TEST_PDF"

# Obtener el contenedor API
API_CONTAINER=$(docker ps -q -f name=ocr-pymupdf-api)

if [ -z "$API_CONTAINER" ]; then
    echo "Error: El contenedor de la API no está en ejecución"
    exit 1
fi

# Obtener la IP del contenedor
API_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $API_CONTAINER)
echo "IP del contenedor API: $API_IP"

# Probar la ruta directamente en el contenedor
echo "Probando ruta POST /api/documents..."
docker exec $API_CONTAINER curl -v -X POST \
    -H "Content-Type: multipart/form-data" \
    -F "file=@/app/$TEST_PDF" \
    "http://localhost:8000/api/documents"

echo ""
echo "Probando ruta POST /api/documents/ (con barra final)..."
docker exec $API_CONTAINER curl -v -X POST \
    -H "Content-Type: multipart/form-data" \
    -F "file=@/app/$TEST_PDF" \
    "http://localhost:8000/api/documents/"

echo ""
echo "Información sobre las rutas configuradas en FastAPI:"
docker exec $API_CONTAINER python -c "
import sys
sys.path.append('/app')
from adapters.inbound.http.api.app import app
print('Rutas configuradas:')
for route in app.routes:
    print(f'- {route.path} [{route.methods}]')
"
