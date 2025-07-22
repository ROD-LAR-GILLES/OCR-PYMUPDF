#!/bin/bash

# Script para configurar los permisos y preparar la interfaz web

# Definir colores para mensajes
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Directorio base del proyecto
BASE_DIR="$(dirname "$(dirname "$0")")/.." # Subir dos niveles desde scripts
BASE_DIR="$(cd "$BASE_DIR" && pwd)" # Obtener ruta absoluta

echo -e "${GREEN}Configurando permisos para los scripts...${NC}"

# Hacer ejecutables los scripts necesarios
chmod +x "$BASE_DIR/tools/bin/run_web.py"
chmod +x "$BASE_DIR/tools/bin/run_web_local.sh"
chmod +x "$BASE_DIR/tools/scripts/build_frontend.sh"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: No se pudieron configurar los permisos.${NC}"
    exit 1
fi

echo -e "${GREEN}Permisos configurados correctamente.${NC}"

# Verificar si existe el directorio de la interfaz web
if [ ! -d "$BASE_DIR/src/interfaces/web" ]; then
    echo -e "${RED}Error: No se encontró el directorio de la interfaz web.${NC}"
    exit 1
fi

# Verificar si existe el directorio del frontend
if [ ! -d "$BASE_DIR/src/interfaces/web/frontend" ]; then
    echo -e "${RED}Error: No se encontró el directorio del frontend.${NC}"
    exit 1
fi

echo -e "${GREEN}Estructura de directorios verificada correctamente.${NC}"
echo -e "${YELLOW}Para construir el frontend, ejecuta: tools/scripts/build_frontend.sh${NC}"
echo -e "${YELLOW}Para iniciar la aplicación web, ejecuta: tools/bin/run_web_local.sh${NC}"