#!/bin/bash

# Script unificado para la gestión del entorno de desarrollo de OCR-PYMUPDF

# Colores para mensajes
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Función de ayuda
show_help() {
    echo -e "${GREEN}OCR-PYMUPDF - Gestión del entorno de desarrollo${NC}"
    echo -e "Uso: $0 [comando]"
    echo -e "\nComandos disponibles:"
    echo -e "  ${YELLOW}start${NC}\t\tIniciar el entorno de desarrollo con Docker"
    echo -e "  ${YELLOW}stop${NC}\t\tDetener el entorno de desarrollo"
    echo -e "  ${YELLOW}test${NC}\t\tEjecutar tests"
    echo -e "  ${YELLOW}docs${NC}\t\tIniciar servidor de documentación"
    echo -e "  ${YELLOW}lint${NC}\t\tEjecutar linters"
    echo -e "  ${YELLOW}deps${NC}\t\tActualizar dependencias"
    echo -e "  ${YELLOW}shell${NC}\t\tEntrar al contenedor"
    echo -e "  ${YELLOW}help${NC}\t\tMostrar esta ayuda"
    echo -e "\nEjemplos:"
    echo -e "  $0 start\t# Iniciar el entorno de desarrollo"
    echo -e "  $0 test\t# Ejecutar tests"
}

# Verificar si Docker está corriendo
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}Error: Docker no está corriendo. Por favor, inicia Docker primero.${NC}"
        exit 1
    fi
}

# Iniciar el entorno de desarrollo
start_dev() {
    check_docker
    echo -e "${GREEN}Iniciando entorno de desarrollo OCR-PYMUPDF...${NC}"
    docker-compose up --build -d
    
    if [ $? -eq 0 ]; then
        echo -e "\n${GREEN}Contenedor iniciado correctamente.${NC}"
        echo -e "\nComandos disponibles:"
        echo -e "${YELLOW}1. Ejecutar tests:${NC} $0 test"
        echo -e "${YELLOW}2. Iniciar documentación:${NC} $0 docs"
        echo -e "${YELLOW}3. Actualizar dependencias:${NC} $0 deps"
        echo -e "${YELLOW}4. Ejecutar linters:${NC} $0 lint"
        echo -e "${YELLOW}5. Entrar al contenedor:${NC} $0 shell"
        echo -e "\n${GREEN}Para detener el contenedor:${NC} $0 stop"
    else
        echo -e "${RED}Error al iniciar el entorno de desarrollo.${NC}"
    fi
}

# Detener el entorno de desarrollo
stop_dev() {
    check_docker
    echo -e "${GREEN}Deteniendo entorno de desarrollo...${NC}"
    docker-compose down
    echo -e "${GREEN}Entorno de desarrollo detenido.${NC}"
}

# Ejecutar tests
run_tests() {
    check_docker
    echo -e "${GREEN}Ejecutando tests...${NC}"
    docker-compose exec ocr-pymupdf pytest
}

# Iniciar servidor de documentación
run_docs() {
    check_docker
    echo -e "${GREEN}Iniciando servidor de documentación...${NC}"
    docker-compose exec ocr-pymupdf mkdocs serve -a 0.0.0.0:8000
    echo -e "${GREEN}Documentación disponible en http://localhost:8000${NC}"
}

# Ejecutar linters
run_lint() {
    check_docker
    echo -e "${GREEN}Ejecutando linters...${NC}"
    docker-compose exec ocr-pymupdf pre-commit run --all-files
}

# Actualizar dependencias
update_deps() {
    check_docker
    echo -e "${GREEN}Actualizando dependencias...${NC}"
    docker-compose exec ocr-pymupdf ./tools/scripts/deps.sh
}

# Entrar al contenedor
enter_shell() {
    check_docker
    echo -e "${GREEN}Entrando al contenedor...${NC}"
    docker-compose exec ocr-pymupdf bash
}

# Procesar comandos
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

case "$1" in
    start)
        start_dev
        ;;
    stop)
        stop_dev
        ;;
    test)
        run_tests
        ;;
    docs)
        run_docs
        ;;
    lint)
        run_lint
        ;;
    deps)
        update_deps
        ;;
    shell)
        enter_shell
        ;;
    help)
        show_help
        ;;
    *)
        echo -e "${RED}Comando desconocido: $1${NC}"
        show_help
        exit 1
        ;;
esac