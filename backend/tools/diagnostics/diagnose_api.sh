#!/bin/bash
# Script para diagnosticar problemas con la API

echo "Diagnosticando API de OCR-PYMUPDF..."

# Obtener el contenedor API
API_CONTAINER=$(docker ps -q -f name=ocr-pymupdf-api)

if [ -z "$API_CONTAINER" ]; then
    echo "Error: El contenedor de la API no está en ejecución"
    exit 1
fi

echo "=== INFORMACIÓN DEL CONTENEDOR ==="
docker inspect $API_CONTAINER | grep -E '(Name|Image|Status|IPAddress|Port)'

echo ""
echo "=== VARIABLES DE ENTORNO LLM ==="
docker exec $API_CONTAINER env | grep -E '(API_KEY|MODEL)'

echo ""
echo "=== RUTAS FASTAPI CONFIGURADAS ==="
docker exec $API_CONTAINER python -c "
import sys
sys.path.append('/app')
from adapters.inbound.http.api.app import app
print('Rutas configuradas:')
for route in app.routes:
    print(f'- {route.path} [{route.methods}]')
"

echo ""
echo "=== ESTADO DE ENDPOINTS ==="
echo "GET /health:"
docker exec $API_CONTAINER curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health
echo ""

echo "GET /api/health:"
docker exec $API_CONTAINER curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health
echo ""

echo "=== ARCHIVOS DE RUTAS ==="
docker exec $API_CONTAINER find /app/src -name "*routes.py" -type f -exec echo {} \; -exec cat {} \; | grep -B 5 -A 1 "@router.post"

echo ""
echo "=== LOGS RECIENTES ==="
docker logs --tail 50 $API_CONTAINER
