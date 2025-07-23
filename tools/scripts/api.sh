#!/bin/bash

# Script para ejecutar la API REST de OCR-PYMUPDF en modo local

# Colores para mensajes
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Función de ayuda
show_help() {
    echo -e "${GREEN}OCR-PYMUPDF API - Script de ejecución local${NC}"
    echo -e "Uso: $0 [opciones]"
    echo -e "\nOpciones:"
    echo -e "  ${YELLOW}--help${NC}\t\tMostrar esta ayuda"
    echo -e "\nNota: Para ejecutar con Docker, use 'docker compose up -d' en la raíz del proyecto."
    echo -e "\nEjemplo:"
echo -e "  $0\t# Ejecutar la API localmente"
}

# Verificar si existe el archivo .env
check_env_file() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}El archivo .env no existe. Creando a partir de .env.example...${NC}"
        cp .env.example .env
        echo -e "${YELLOW}Por favor, edita el archivo .env con tus configuraciones antes de continuar.${NC}"
        exit 1
    fi
}

# Crear directorios necesarios
create_directories() {
    echo -e "${GREEN}Creando directorios necesarios...${NC}"
    mkdir -p uploads results metadata
}

# Ejecutar la API en modo local
run_local() {
    check_env_file
    create_directories
    echo -e "${GREEN}Iniciando API en modo local...${NC}"
    python3 tools/bin/run_api.py
}



# Procesar argumentos
if [ $# -eq 0 ]; then
    # Sin argumentos, ejecutar en modo local por defecto
    run_local
    exit 0
fi

case "$1" in
    --help)
        show_help
        ;;
    *)
        echo -e "${RED}Opción desconocida: $1${NC}"
        show_help
        exit 1
        ;;
esac