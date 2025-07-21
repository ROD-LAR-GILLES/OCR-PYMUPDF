#!/bin/bash

# Colores para mensajes
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo -e "${GREEN}Iniciando entorno de desarrollo OCR-PYMUPDF...${NC}\n"

# Verificar si Docker está corriendo
if ! docker info > /dev/null 2>&1; then
    echo -e "${YELLOW}Error: Docker no está corriendo. Por favor, inicia Docker primero.${NC}"
    exit 1

fi

# Construir y levantar contenedores
echo -e "${GREEN}Construyendo y levantando contenedores...${NC}"
docker-compose up --build -d

# Verificar si el contenedor se levantó correctamente
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}Contenedor iniciado correctamente.${NC}"
    echo -e "\nComandos disponibles:"
    echo -e "${YELLOW}1. Ejecutar tests:${NC} docker-compose exec ocr-pymupdf pytest"
    echo -e "${YELLOW}2. Iniciar documentación:${NC} docker-compose exec ocr-pymupdf mkdocs serve -a 0.0.0.0:8000"
    echo -e "${YELLOW}3. Actualizar dependencias:${NC} docker-compose exec ocr-pymupdf ./scripts/update_dependencies.sh"
    echo -e "${YELLOW}4. Ejecutar linters:${NC} docker-compose exec ocr-pymupdf pre-commit run --all-files"
    echo -e "${YELLOW}5. Entrar al contenedor:${NC} docker-compose exec ocr-pymupdf bash"
    echo -e "\n${GREEN}Para detener el contenedor:${NC} docker-compose down"
else
    echo -e "${YELLOW}Error: No se pudo iniciar el contenedor.${NC}"
    exit 1
fi
