#!/bin/bash
# Script para analizar problemas de código como lo hace VS Code

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}  Analizando código - problemas como VS Code${NC}"
echo "=================================================="

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

# Función para ejecutar flake8 (linting como VS Code)
run_flake8() {
    echo ""
    echo -e "${YELLOW}  Ejecutando Flake8 (Linting y estilo)...${NC}"
    echo "============================================"
    
    docker exec $API_CONTAINER flake8 /app/src \
        --max-line-length=120 \
        --ignore=E501,W503,E203,F401 \
        --exclude=__pycache__,*.pyc,.git,venv,env \
        --show-source \
        --statistics \
        --format='%(path)s:%(row)d:%(col)d: %(code)s %(text)s' || true
}

# Función para ejecutar MyPy
run_mypy() {
    echo ""
    echo -e "${YELLOW}� Ejecutando MyPy...${NC}"
    echo "======================"
    
    docker exec $API_CONTAINER mypy /app/src 
        --ignore-missing-imports 
        --follow-imports=skip 
        --show-column-numbers 
        --no-error-summary || true
        
    echo -e "${GREEN}  MyPy completado${NC}"
}

# Función para mostrar errores de importación
check_imports() {
    echo ""
    echo -e "${YELLOW}  Verificando importaciones...${NC}"
    echo "=================================="
    
    # Verificar que no hay errores de importación básicos
    docker exec $API_CONTAINER python -c "
import sys
sys.path.append('/app')

# Lista de módulos principales a verificar
modules_to_check = [
    'src.main',
    'src.adapters.inbound.http.api.app',
    'src.adapters.out.ocr.pymupdf_adapter',
    'src.domain.use_cases.pdf_to_markdown',
    'src.infrastructure.logging_setup'
]

errors = []
for module in modules_to_check:
    try:
        __import__(module)
        print(f'  {module}')
    except Exception as e:
        print(f'  {module}: {e}')
        errors.append((module, str(e)))

if errors:
    print(f'\n  Se encontraron {len(errors)} errores de importación')
    for module, error in errors:
        print(f'   {module}: {error}')
else:
    print(f'\n  Todas las importaciones están correctas')
" || true
}

# Función para verificar sintaxis Python
check_syntax() {
    echo ""
    echo -e "${YELLOW}  Verificando sintaxis Python...${NC}"
    echo "=================================="
    
    docker exec $API_CONTAINER find /app/src -name "*.py" -exec python -m py_compile {} \; 2>&1 | grep -v "^$" || echo -e "${GREEN}  No hay errores de sintaxis${NC}"
}

# Función para mostrar estadísticas del código
show_stats() {
    echo ""
    echo -e "${BLUE}  Estadísticas del código:${NC}"
    echo "=========================="
    
    docker exec $API_CONTAINER bash -c "
    echo 'Archivos Python:'
    find /app/src -name '*.py' | wc -l
    echo 'Líneas totales de código:'
    find /app/src -name '*.py' -exec cat {} \; | wc -l
    echo 'Archivos por directorio:'
    find /app/src -type d -exec bash -c 'echo -n \"{}: \"; find \"{}\" -maxdepth 1 -name \"*.py\" | wc -l' \;
    "
}

# Función principal
main() {
    # Procesar argumentos
    QUICK_MODE=false
    SPECIFIC_FILE=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --quick|-q)
                QUICK_MODE=true
                shift
                ;;
            --file|-f)
                SPECIFIC_FILE="$2"
                shift 2
                ;;
            --help|-h)
                echo "Uso: $0 [opciones]"
                echo "Opciones:"
                echo "  --quick, -q     Ejecutar solo verificaciones rápidas"
                echo "  --file, -f      Analizar un archivo específico"
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
    
    if [ ! -z "$SPECIFIC_FILE" ]; then
        echo -e "${BLUE}  Analizando archivo específico: $SPECIFIC_FILE${NC}"
        docker exec $API_CONTAINER flake8 "/app/$SPECIFIC_FILE" --show-source || true
        docker exec $API_CONTAINER mypy "/app/$SPECIFIC_FILE" --ignore-missing-imports || true
        return
    fi
    
    if [ "$QUICK_MODE" = true ]; then
        echo -e "${BLUE}  Modo rápido activado${NC}"
        check_syntax
        check_imports
    else
        check_syntax
        check_imports
        run_flake8
        run_mypy
        show_stats
    fi
    
    echo ""
    echo -e "${GREEN}  Análisis completado${NC}"
    echo "  Tip: Usa --quick para análisis rápido o --file <archivo> para un archivo específico"
}

# Ejecutar función principal con todos los argumentos
main "$@"
