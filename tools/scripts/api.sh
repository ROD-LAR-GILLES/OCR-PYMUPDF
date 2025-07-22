#!/bin/bash

# Script unificado para la API REST de OCR-PYMUPDF
# Permite ejecutar la API en modo local o con Docker

# Colores para mensajes
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Función de ayuda
show_help() {
    echo -e "${GREEN}OCR-PYMUPDF API - Script de ejecución unificado${NC}"
    echo -e "Uso: $0 [opciones]"
    echo -e "\nOpciones:"
    echo -e "  ${YELLOW}--local${NC}\t\tEjecutar la API en modo local (predeterminado)"
    echo -e "  ${YELLOW}--docker${NC}\t\tEjecutar la API usando Docker"
    echo -e "  ${YELLOW}--stop${NC}\t\tDetener la API en Docker"
    echo -e "  ${YELLOW}--help${NC}\t\tMostrar esta ayuda"
    echo -e "\nEjemplos:"
    echo -e "  $0 --local\t# Ejecutar la API localmente"
    echo -e "  $0 --docker\t# Ejecutar la API con Docker"
    echo -e "  $0 --stop\t# Detener la API en Docker"
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
    python bin/run_api.py
}

# Ejecutar la API con Docker
run_docker() {
    check_env_file
    create_directories
    echo -e "${GREEN}Iniciando API con Docker...${NC}"
    docker-compose -f docker-compose.api.yml up --build -d
    echo -e "${GREEN}API REST de OCR-PYMUPDF iniciada en http://localhost:8000${NC}"
    echo -e "${GREEN}Documentación disponible en http://localhost:8000/docs${NC}"
}

# Detener la API en Docker
stop_docker() {
    echo -e "${GREEN}Deteniendo API en Docker...${NC}"
    docker-compose -f docker-compose.api.yml down
    echo -e "${GREEN}API detenida correctamente.${NC}"
}

# Procesar argumentos
if [ $# -eq 0 ]; then
    # Sin argumentos, ejecutar en modo local por defecto
    run_local
    exit 0
fi

case "$1" in
    --local)
        run_local
        ;;
    --docker)
        run_docker
        ;;
    --stop)
        stop_docker
        ;;
    --help)
        show_help
        ;;
    *)
        echo -e "${RED}Opción desconocida: $1${NC}"
        show_help
        exit 1
        ;;
esac