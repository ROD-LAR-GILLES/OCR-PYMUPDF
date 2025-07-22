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
    echo -e "  ${YELLOW}update${NC}\t\tActualizar todas las dependencias (predeterminado)"
    echo -e "  ${YELLOW}base${NC}\t\tActualizar solo dependencias base"
    echo -e "  ${YELLOW}dev${NC}\t\tActualizar solo dependencias de desarrollo"
    echo -e "  ${YELLOW}api${NC}\t\tActualizar solo dependencias de la API"
    echo -e "  ${YELLOW}docs${NC}\t\tActualizar solo dependencias de documentación"
    echo -e "  ${YELLOW}check${NC}\t\tVerificar vulnerabilidades de seguridad"
    echo -e "  ${YELLOW}sync${NC}\t\tSincronizar el entorno virtual con las dependencias"
    echo -e "  ${YELLOW}help${NC}\t\tMostrar esta ayuda"
    echo -e "\nEjemplos:"
    echo -e "  $0 update\t# Actualizar todas las dependencias"
    echo -e "  $0 dev\t# Actualizar solo dependencias de desarrollo"
}

# Asegurar que estamos en la raíz del proyecto
cd "$(dirname "$0")/../../" || exit 1

# Verificar si pip-tools está instalado
check_pip_tools() {
    if ! command -v pip-compile &> /dev/null; then
        echo -e "${YELLOW}Instalando pip-tools...${NC}"
        pip install pip-tools
    fi
}

# Actualizar dependencias base
update_base() {
    echo -e "${GREEN}Actualizando dependencias base...${NC}"
    pip-compile --upgrade --output-file requirements/base.txt requirements/requirements.in
}

# Actualizar dependencias de desarrollo
update_dev() {
    echo -e "${GREEN}Actualizando dependencias de desarrollo...${NC}"
    pip-compile --upgrade --output-file requirements/dev.txt requirements/requirements-dev.in
}

# Actualizar dependencias de la API
update_api() {
    echo -e "${GREEN}Actualizando dependencias de la API...${NC}"
    pip-compile --upgrade --output-file requirements/api.txt requirements/api.in
}

# Actualizar dependencias de documentación
update_docs() {
    echo -e "${GREEN}Actualizando dependencias de documentación...${NC}"
    pip-compile --upgrade --output-file requirements/docs.txt requirements/docs.in
}

# Verificar vulnerabilidades de seguridad
check_security() {
    echo -e "${GREEN}Verificando vulnerabilidades de seguridad...${NC}"
    if command -v safety &> /dev/null; then
        safety check -r requirements/base.txt
        safety check -r requirements/dev.txt
        safety check -r requirements/api.txt
        safety check -r requirements/docs.txt
    else
        echo -e "${YELLOW}Safety no está instalado. Instálalo con: pip install safety${NC}"
    fi
}

# Sincronizar el entorno virtual con las dependencias
sync_env() {
    echo -e "${GREEN}Sincronizando entorno virtual...${NC}"
    if command -v pip-sync &> /dev/null; then
        pip-sync requirements/base.txt requirements/dev.txt requirements/api.txt requirements/docs.txt
    else
        echo -e "${YELLOW}Instalando dependencias manualmente...${NC}"
        pip install -r requirements/base.txt -r requirements/dev.txt -r requirements/api.txt -r requirements/docs.txt
    fi
}

# Actualizar todas las dependencias
update_all() {
    update_base
    update_dev
    update_api
    update_docs
    check_security
    sync_env
}

# Verificar pip-tools
check_pip_tools

# Procesar comandos
if [ $# -eq 0 ]; then
    # Sin argumentos, actualizar todas las dependencias por defecto
    update_all
    exit 0
fi

case "$1" in
    update)
        update_all
        ;;
    base)
        update_base
        ;;
    dev)
        update_dev
        ;;
    api)
        update_api
        ;;
    docs)
        update_docs
        ;;
    check)
        check_security
        ;;
    sync)
        sync_env
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