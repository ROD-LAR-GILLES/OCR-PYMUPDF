#!/bin/bash
# Script para formatear código automáticamente

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}   Formateando código automáticamente${NC}"
echo "=============================================="

# Función para verificar si el contenedor está corriendo
check_container() {
    API_CONTAINER=$(docker ps -q -f name=ocr-pymupdf-api)
    if [ -z "$API_CONTAINER" ]; then
        echo -e "${RED}  Error: El contenedor de la API no está en ejecución${NC}"
        echo "Iniciando contenedor..."
        docker-compose up -d
        sleep 10
        API_CONTAINER=$(docker ps -q -f name=ocr-pymupdf-api)
        if [ -z "$API_CONTAINER" ]; then
            echo -e "${RED}  No se pudo iniciar el contenedor${NC}"
            exit 1
        fi
    fi
    echo -e "${GREEN}  Contenedor encontrado: $API_CONTAINER${NC}"
}

# Función para formatear con black
format_with_black() {
    echo ""
    echo -e "${YELLOW}  Formateando con Black...${NC}"
    echo "=============================="
    
    docker exec $API_CONTAINER black /app/src \
        --line-length=120 \
        --target-version=py311 \
        --include='\.pyi?$' \
        --extend-exclude='__pycache__|\.git|\.pytest_cache|\.mypy_cache' \
        --diff \
        --color || true
        
    echo -e "${GREEN}  Formateo con Black completado${NC}"
}

# Función para aplicar cambios con black
apply_black_formatting() {
    echo ""
    echo -e "${YELLOW}  Aplicando formateo con Black...${NC}"
    echo "==================================="
    
    docker exec $API_CONTAINER black /app/src \
        --line-length=120 \
        --target-version=py311 \
        --include='\.pyi?$' \
        --extend-exclude='__pycache__|\.git|\.pytest_cache|\.mypy_cache' \
        --quiet
        
    echo -e "${GREEN}  Formateo aplicado${NC}"
}

# Función para ordenar imports con isort
sort_imports() {
    echo ""
    echo -e "${YELLOW}  Ordenando imports con isort...${NC}"
    echo "=================================="
    
    # Instalar isort si no está disponible
    docker exec $API_CONTAINER pip install isort || true
    
    docker exec $API_CONTAINER isort /app/src \
        --profile=black \
        --line-length=120 \
        --multi-line=3 \
        --trailing-comma \
        --force-grid-wrap=0 \
        --combine-as \
        --diff \
        --color || true
        
    echo -e "${GREEN}  Imports ordenados${NC}"
}

# Función para aplicar cambios de isort
apply_import_sorting() {
    echo ""
    echo -e "${YELLOW}  Aplicando ordenamiento de imports...${NC}"
    echo "========================================"
    
    docker exec $API_CONTAINER isort /app/src \
        --profile=black \
        --line-length=120 \
        --multi-line=3 \
        --trailing-comma \
        --force-grid-wrap=0 \
        --combine-as \
        --quiet
        
    echo -e "${GREEN}  Ordenamiento de imports aplicado${NC}"
}

# Función para arreglar problemas básicos de flake8
fix_basic_issues() {
    echo ""
    echo -e "${YELLOW}  Instalando autopep8...${NC}"
    docker exec $API_CONTAINER pip install autopep8 || true
    
    echo -e "${YELLOW}  Arreglando problemas básicos con autopep8...${NC}"
    echo "==============================================="
    
    docker exec $API_CONTAINER autopep8 /app/src \
        --recursive \
        --in-place \
        --aggressive \
        --aggressive \
        --max-line-length=120 \
        --ignore=E501 \
        --select=E1,E2,E3,W1,W2,W3
        
    echo -e "${GREEN}  Problemas básicos arreglados${NC}"
}

# Función para mostrar estadísticas después del formateo
show_stats() {
    echo ""
    echo -e "${BLUE}  Estadísticas después del formateo:${NC}"
    echo "====================================="
    
    # Ejecutar flake8 solo para contar errores
    ERRORS=$(docker exec $API_CONTAINER flake8 /app/src \
        --max-line-length=120 \
        --ignore=E501,W503,E203 \
        --exclude=__pycache__,*.pyc,.git,venv,env \
        --count \
        --statistics 2>/dev/null | tail -1 || echo "0")
    
    echo -e "Errores restantes de flake8: ${ERRORS:-0}"
}

# Función principal
main() {
    # Procesar argumentos
    DRY_RUN=false
    APPLY_CHANGES=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --apply)
                APPLY_CHANGES=true
                shift
                ;;
            --help|-h)
                echo "Uso: $0 [opciones]"
                echo "Opciones:"
                echo "  --dry-run       Solo mostrar cambios, no aplicar"
                echo "  --apply         Aplicar todos los cambios automáticamente"
                echo "  --help, -h      Mostrar esta ayuda"
                exit 0
                ;;
            *)
                echo "Opción desconocida: $1"
                exit 1
                ;;
        esac
    done
    
    check_container
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "${BLUE}  Modo dry-run: Solo mostrando cambios${NC}"
        format_with_black
        sort_imports
    elif [ "$APPLY_CHANGES" = true ]; then
        echo -e "${BLUE}  Aplicando cambios automáticamente${NC}"
        fix_basic_issues
        apply_import_sorting
        apply_black_formatting
        show_stats
    else
        echo -e "${YELLOW}  ¿Qué deseas hacer?${NC}"
        echo "1) Ver cambios sin aplicar (dry-run)"
        echo "2) Aplicar formateo automático"
        echo "3) Solo arreglar problemas básicos"
        echo "4) Salir"
        
        read -p "Selecciona una opción [1-4]: " choice
        
        case $choice in
            1)
                echo -e "${BLUE}  Mostrando cambios...${NC}"
                format_with_black
                sort_imports
                ;;
            2)
                echo -e "${BLUE}  Aplicando formateo completo...${NC}"
                fix_basic_issues
                apply_import_sorting
                apply_black_formatting
                show_stats
                ;;
            3)
                echo -e "${BLUE}  Arreglando solo problemas básicos...${NC}"
                fix_basic_issues
                show_stats
                ;;
            4)
                echo -e "${GREEN}  ¡Hasta luego!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}  Opción inválida${NC}"
                exit 1
                ;;
        esac
    fi
    
    echo ""
    echo -e "${GREEN}  Formateo completado${NC}"
    echo "  Tip: Ejecuta './tools/lint_code.sh --quick' para verificar los cambios"
}

# Ejecutar función principal con todos los argumentos
main "$@"
