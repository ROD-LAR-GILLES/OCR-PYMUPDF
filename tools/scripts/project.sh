#!/bin/bash

# Script unificado para la gestión del proyecto OCR-PYMUPDF

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
    echo -e "  ${YELLOW}reorganize${NC}\tReorganizar la estructura del proyecto"
    echo -e "  ${YELLOW}cleanup${NC}\t\tEliminar archivos duplicados después de la reorganización"
    echo -e "  ${YELLOW}update-refs${NC}\tActualizar referencias en el código"
    echo -e "  ${YELLOW}status${NC}\t\tMostrar el estado actual del proyecto"
    echo -e "  ${YELLOW}help${NC}\t\tMostrar esta ayuda"
}

# Asegurar que estamos en la raíz del proyecto
cd "$(dirname "$0")/../../" || exit 1

# Función para reorganizar el proyecto
reorganize_project() {
    echo -e "${BLUE}=================================================================${NC}"
    echo -e "${BLUE}      REORGANIZACIÓN DEL PROYECTO OCR-PYMUPDF${NC}"
    echo -e "${BLUE}=================================================================${NC}"
    echo ""
    echo "Este script realizará la reorganización del proyecto según la nueva estructura."
    echo "El proceso se divide en varias etapas:"
    echo ""
    echo "1. Creación de la nueva estructura de directorios"
    echo "2. Copia de archivos a sus nuevas ubicaciones"
    echo "3. Actualización de referencias en el código"
    echo "4. Verificación del funcionamiento"
    echo "5. Limpieza de archivos duplicados"
    echo ""
    echo -e "${YELLOW}IMPORTANTE: Se recomienda hacer un respaldo del proyecto antes de continuar.${NC}"
    echo ""

    read -p "¿Desea continuar con la reorganización? (s/n): " respuesta
    if [[ "$respuesta" != "s" && "$respuesta" != "S" ]]; then
        echo "Reorganización cancelada."
        return 1
    fi

    echo ""
    echo -e "${GREEN}=== ETAPA 1: Creación de la nueva estructura de directorios ===${NC}"
    echo ""

    mkdir -p .config/flake8 .config/mypy .config/pytest .config/tox .config/pre-commit \
           docs/api docs/user docs/developer \
           scripts/data scripts/deployment scripts/maintenance \
           data/dictionaries data/corrections data/config \
           requirements bin \
           tools/scripts tools/bin

    echo "Estructura de directorios creada con éxito."

    echo ""
    echo -e "${GREEN}=== ETAPA 2: Copia de archivos a sus nuevas ubicaciones ===${NC}"
    echo ""

    # Archivos de configuración
    cp .flake8 .config/flake8/ && \
    cp mypy.ini .config/mypy/ && \
    cp pytest.ini .config/pytest/ && \
    cp tox.ini .config/tox/ && \
    cp .pre-commit-config.yaml .config/pre-commit/

    # Documentación
    cp docs/api.md docs/api/ && \
    cp docs/docs/index.md docs/user/ && \
    cp CONTRIBUTING.md docs/developer/contributing.md && \
    touch docs/developer/architecture.md

    # Scripts
    cp scripts/legal_dictionary_manager.py scripts/data/ && \
    cp scripts/update_dependencies.sh scripts/maintenance/ && \
    cp run_api_docker.sh scripts/deployment/

    # Datos
    cp data/legal_words.txt data/legal_patterns.txt data/dictionaries/ && \
    cp data/corrections.csv data/corrections/ && \
    cp data/ocr.json data/config/

    # Requisitos
    cp requirements/requirements.txt requirements/base.txt && \
    cp requirements/api-requirements.txt requirements/api.txt && \
    cp requirements/requirements-dev.txt requirements/dev.txt && \
    touch requirements/docs.txt

    # Archivos de ejecución
    cp run_api.py run_api_local.sh start.sh bin/

    # Crear scripts unificados en tools/
    echo "Creando scripts unificados en tools/..."
    
    # Asegurar que los scripts en tools/ son ejecutables
    chmod +x tools/scripts/*.sh 2>/dev/null
    chmod +x tools/bin/*.py 2>/dev/null

    echo "Archivos copiados a sus nuevas ubicaciones con éxito."

    echo ""
    echo -e "${GREEN}=== ETAPA 3: Actualización de referencias en el código ===${NC}"
    echo ""

    read -p "¿Desea actualizar las referencias en el código? (s/n): " respuesta
    if [[ "$respuesta" == "s" || "$respuesta" == "S" ]]; then
        update_references
    else
        echo "Actualización de referencias omitida."
    fi

    echo ""
    echo -e "${GREEN}=== ETAPA 4: Verificación del funcionamiento ===${NC}"
    echo ""

    echo "Ahora debe verificar que el proyecto funcione correctamente con la nueva estructura."
    echo "Se recomienda ejecutar las pruebas y verificar que la aplicación se inicie correctamente."
    echo ""
    echo "Comandos sugeridos para verificar:"
    echo "- python -m pytest  # Ejecutar pruebas"
    echo "- bash tools/scripts/dev.sh start  # Iniciar la aplicación"
    echo ""

    read -p "¿Ha verificado que todo funciona correctamente? (s/n): " respuesta
    if [[ "$respuesta" != "s" && "$respuesta" != "S" ]]; then
        echo "Por favor, verifique el funcionamiento antes de continuar con la limpieza."
        echo "Puede ejecutar este script nuevamente más tarde para completar el proceso."
        return 1
    fi

    echo ""
    echo -e "${GREEN}=== ETAPA 5: Limpieza de archivos duplicados ===${NC}"
    echo ""

    echo -e "${YELLOW}ADVERTENCIA: Esta acción eliminará los archivos originales que han sido copiados a sus nuevas ubicaciones.${NC}"
    echo "Asegúrese de haber verificado que todo funciona correctamente antes de continuar."
    echo ""

    read -p "¿Desea eliminar los archivos duplicados? (s/n): " respuesta
    if [[ "$respuesta" == "s" || "$respuesta" == "S" ]]; then
        cleanup_after_reorganization
    else
        echo "Limpieza omitida. Puede ejecutar 'bash tools/scripts/project.sh cleanup' más tarde."
    fi

    echo ""
    echo -e "${BLUE}=================================================================${NC}"
    echo -e "${BLUE}      REORGANIZACIÓN COMPLETADA${NC}"
    echo -e "${BLUE}=================================================================${NC}"
    echo ""
    echo "La reorganización del proyecto ha sido completada con éxito."
    echo "Consulte ESTRUCTURA_PROYECTO.md para obtener información sobre la nueva estructura."
    echo ""
}

# Función para limpiar archivos duplicados
cleanup_after_reorganization() {
    echo -e "${YELLOW}Eliminando archivos duplicados después de la reorganización...${NC}"

    # Archivos de configuración
    rm -f .flake8
    rm -f mypy.ini
    rm -f pytest.ini
    rm -f tox.ini
    rm -f .pre-commit-config.yaml

    # Documentación
    rm -f docs/api.md
    rm -f CONTRIBUTING.md
    rm -rf docs/docs

    # Scripts
    rm -f scripts/legal_dictionary_manager.py
    rm -f scripts/update_dependencies.sh
    rm -f run_api_docker.sh

    # Datos
    rm -f data/legal_words.txt
    rm -f data/legal_patterns.txt
    rm -f data/corrections.csv
    rm -f data/ocr.json

    # Archivos de ejecución
    rm -f run_api.py
    rm -f run_api_local.sh
    rm -f start.sh

    # Requisitos
    rm -f requirements/api-requirements.txt
    rm -f requirements/requirements-dev.txt
    rm -f requirements/requirements.txt

    echo -e "${GREEN}Limpieza completada. La nueva estructura de directorios está lista.${NC}"
}

# Función para actualizar referencias en el código
update_references() {
    echo -e "${GREEN}Actualizando referencias en el código...${NC}"
    
    # Verificar si el script existe
    if [ -f "scripts/maintenance/update_references.sh" ]; then
        bash scripts/maintenance/update_references.sh
    else
        echo -e "${RED}Error: No se encontró el script de actualización de referencias.${NC}"
        return 1
    fi
}

# Función para mostrar el estado del proyecto
show_status() {
    echo -e "${GREEN}Estado actual del proyecto OCR-PYMUPDF${NC}"
    echo -e "${BLUE}----------------------------------------${NC}"
    
    # Verificar estructura de directorios
    echo -e "${YELLOW}Estructura de directorios:${NC}"
    for dir in .config docs scripts data requirements bin tools; do
        if [ -d "$dir" ]; then
            echo -e "  [${GREEN}✓${NC}] $dir"
        else
            echo -e "  [${RED}✗${NC}] $dir (no existe)"
        fi
    done
    
    echo ""
    echo -e "${YELLOW}Scripts unificados:${NC}"
    for script in tools/scripts/*.sh; do
        if [ -f "$script" ]; then
            echo -e "  [${GREEN}✓${NC}] $script"
        fi
    done
    
    for script in tools/bin/*.py; do
        if [ -f "$script" ]; then
            echo -e "  [${GREEN}✓${NC}] $script"
        fi
    done
    
    echo ""
    echo -e "${YELLOW}Archivos duplicados:${NC}"
    duplicados=0
    
    # Verificar archivos de configuración
    for file in .flake8 mypy.ini pytest.ini tox.ini .pre-commit-config.yaml; do
        if [ -f "$file" ]; then
            echo -e "  [${RED}!${NC}] $file (duplicado)"
            duplicados=$((duplicados+1))
        fi
    done
    
    # Verificar scripts
    for file in scripts/legal_dictionary_manager.py scripts/update_dependencies.sh run_api_docker.sh; do
        if [ -f "$file" ]; then
            echo -e "  [${RED}!${NC}] $file (duplicado)"
            duplicados=$((duplicados+1))
        fi
    done
    
    # Verificar archivos de ejecución
    for file in run_api.py run_api_local.sh start.sh; do
        if [ -f "$file" ]; then
            echo -e "  [${RED}!${NC}] $file (duplicado)"
            duplicados=$((duplicados+1))
        fi
    done
    
    if [ $duplicados -eq 0 ]; then
        echo -e "  [${GREEN}✓${NC}] No se encontraron archivos duplicados"
    fi
}

# Procesar comandos
case "$1" in
    reorganize)
        reorganize_project
        ;;
    cleanup)
        cleanup_after_reorganization
        ;;
    update-refs)
        update_references
        ;;
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