#!/bin/bash

# Script para reiniciar los contenedores después de realizar cambios

echo "Deteniendo contenedores..."
docker-compose down

echo "Reconstruyendo imágenes..."
docker-compose build

echo "Iniciando contenedores..."
docker-compose up -d

echo "Esperando a que los contenedores estén listos..."
sleep 10

echo "Estado de los contenedores:"
docker ps -a | grep ocr-pymupdf

echo "Logs del contenedor API:"
docker logs ocr-pymupdf-api

echo "Logs del contenedor Frontend:"
docker logs ocr-pymupdf-frontend