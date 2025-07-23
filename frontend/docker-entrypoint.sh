#!/bin/sh
# Script de inicialización para el frontend

# Esperar a que la API esté disponible
echo "Esperando a que la API esté disponible..."
until $(curl --output /dev/null --silent --head --fail http://ocr-api:8000/api/health); do
    printf '.'
    sleep 5
done
echo "API está lista!"

# Iniciar nginx
nginx -g "daemon off;"
