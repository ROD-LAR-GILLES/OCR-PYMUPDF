#!/bin/bash

# Script simplificado para la gestión del proyecto OCR-PYMUPDF

# Colores para mensajes
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

# Función de ayuda
show_help() {
    echo -e "${GREEN}OCR-PYMUPDF - Gestión del Proyecto${NC}"
    echo -e "Uso: $0 [comando]"
    echo -e "\nComandos disponibles:"
    echo -e "  ${YELLOW}status${NC}\t\tMostrar el estado actual del proyecto"
    echo -e "  ${YELLOW}help${NC}\t\tMostrar esta ayuda"
}

# Asegurar que estamos en la raíz del proyecto
cd "$(dirname "$0")/../../" || exit 1

# Función para mostrar el estado del proyecto
show_status() {
    echo -e "${GREEN}Estado actual del proyecto OCR-PYMUPDF${NC}"
    echo -e "${BLUE}----------------------------------------${NC}"
    
    # Verificar estructura de directorios
    echo -e "${YELLOW}Estructura de directorios:${NC}"
    for dir in src tools/bin tools/scripts tools/.config tools/tests; do
        if [ -d "$dir" ]; then
            echo -e "  [${GREEN}✓${NC}] $dir"
        else
            echo -e "  [${RED}✗${NC}] $dir (no existe)"
        fi
    done
    
    echo ""
    echo -e "${YELLOW}Scripts principales:${NC}"
    for script in tools/scripts/*.sh; do
        if [ -f "$script" ]; then
            echo -e "  [${GREEN}✓${NC}] $script"
        fi
    done
    
    for script in tools/bin/*.py tools/bin/*.sh; do
        if [ -f "$script" ]; then
            echo -e "  [${GREEN}✓${NC}] $script"
        fi
    done
}

# Procesar comandos
case "$1" in
    status)
        show_status
        ;;
    help)
        show_help
        ;;
    *)
        if [ -z "$1" ]; then
            show_help
        else
            echo -e "${RED}Comando desconocido: $1${NC}"
            show_help
            exit 1
        fi
        ;;
esac