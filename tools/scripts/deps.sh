#!/bin/bash

# Script unificado para la gestión de dependencias de OCR-PYMUPDF

# Colores para mensajes
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Función de ayuda
show_help() {
    echo -e "${GREEN}OCR-PYMUPDF - Gestión de dependencias${NC}"
    echo -e "Uso: $0 [comando]"
    echo -e "\nComandos disponibles:"
    echo -e "  ${YELLOW}update${NC}\t\tActualizar dependencias (predeterminado)"
    echo -e "  ${YELLOW}check${NC}\t\tVerificar vulnerabilidades de seguridad"
    echo -e "  ${YELLOW}help${NC}\t\tMostrar esta ayuda"
    echo -e "\nEjemplos:"
    echo -e "  $0 update\t# Actualizar dependencias"
    echo -e "  $0 check\t# Verificar vulnerabilidades de seguridad"
}

# Asegurar que estamos en la raíz del proyecto
cd "$(dirname "$0")/../../" || exit 1

# Actualizar dependencias
update_deps() {
    echo -e "${GREEN}Actualizando dependencias...${NC}"
    pip install --upgrade -r requirements.txt
}

# Verificar vulnerabilidades de seguridad
check_security() {
    echo -e "${GREEN}Verificando vulnerabilidades de seguridad...${NC}"
    if command -v safety &> /dev/null; then
        safety check -r requirements.txt
    else
        echo -e "${YELLOW}Safety no está instalado. Instálalo con: pip install safety${NC}"
        pip install safety
        safety check -r requirements.txt
    fi
}

# Procesar comandos
if [ $# -eq 0 ]; then
    # Sin argumentos, actualizar dependencias por defecto
    update_deps
    exit 0
fi

case "$1" in
    update)
        update_deps
        ;;
    check)
        check_security
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