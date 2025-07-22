#!/bin/bash

# Script para construir el frontend de OCR-PYMUPDF

# Definir colores para mensajes
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Directorio del frontend
FRONTEND_DIR="$(dirname "$(dirname "$0")")/.." # Subir dos niveles desde scripts
FRONTEND_DIR="$FRONTEND_DIR/src/interfaces/web/frontend"

# Verificar si el directorio existe
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}Error: No se encontró el directorio del frontend en $FRONTEND_DIR${NC}"
    exit 1
fi

# Ir al directorio del frontend
cd "$FRONTEND_DIR" || exit 1

# Verificar si npm está instalado
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm no está instalado. Por favor, instala Node.js y npm.${NC}"
    exit 1
fi

echo -e "${GREEN}Instalando dependencias...${NC}"

# Instalar dependencias
npm install

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: No se pudieron instalar las dependencias.${NC}"
    exit 1
fi

echo -e "${GREEN}Construyendo el frontend...${NC}"

# Construir el frontend
npm run build

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: No se pudo construir el frontend.${NC}"
    exit 1
fi

echo -e "${GREEN}Frontend construido correctamente.${NC}"

# Verificar si el directorio dist existe
if [ ! -d "$FRONTEND_DIR/dist" ]; then
    echo -e "${RED}Error: No se encontró el directorio dist después de la construcción.${NC}"
    exit 1
fi

echo -e "${GREEN}El frontend está listo para ser servido por la API web.${NC}"
echo -e "${YELLOW}Para iniciar la aplicación web, ejecuta: tools/bin/run_web_local.sh${NC}"