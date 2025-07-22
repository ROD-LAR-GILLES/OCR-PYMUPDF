#!/bin/bash

# Script para iniciar la interfaz web de OCR-PYMUPDF en modo local

# Definir colores para mensajes
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Verificar si Python está instalado
if ! command -v python &> /dev/null; then
    echo -e "${RED}Error: Python no está instalado.${NC}"
    exit 1
fi

# Verificar si el entorno virtual está activado
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}Advertencia: No se detectó un entorno virtual activo.${NC}"
    echo -e "${YELLOW}Se recomienda activar un entorno virtual antes de ejecutar este script.${NC}"
    read -p "¿Desea continuar de todos modos? (s/n): " response
    if [[ "$response" != "s" ]]; then
        exit 0
    fi
fi

# Configurar variables de entorno para desarrollo local
export WEB_HOST="127.0.0.1"
export WEB_PORT="8080"

echo -e "${GREEN}Iniciando la interfaz web de OCR-PYMUPDF en modo local...${NC}"
echo -e "${GREEN}La interfaz estará disponible en: http://$WEB_HOST:$WEB_PORT${NC}"

# Ejecutar la aplicación web
python "$(dirname "$0")/run_web.py"