#!/bin/bash
# Herramienta para ejecutar tests unitarios y de integración

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Ejecutando Tests - OCR-PYMUPDF${NC}"
echo "======================================="

# Función para verificar si el contenedor está corriendo
check_container() {
    API_CONTAINER=$(docker ps -q -f name=ocr-pymupdf-api)
    if [ -z "$API_CONTAINER" ]; then
        echo -e "${RED}❌ Error: El contenedor de la API no está en ejecución${NC}"
        echo "Iniciando contenedor..."
        docker-compose up -d
        sleep 10
        API_CONTAINER=$(docker ps -q -f name=ocr-pymupdf-api)
        if [ -z "$API_CONTAINER" ]; then
            echo -e "${RED}❌ No se pudo iniciar el contenedor${NC}"
            exit 1
        fi
    fi
    echo -e "${GREEN}✅ Contenedor encontrado: $API_CONTAINER${NC}"
}

# Función para instalar pytest si no está disponible
install_pytest() {
    echo -e "${YELLOW}📦 Verificando pytest...${NC}"
    if ! docker exec $API_CONTAINER python -c "import pytest" 2>/dev/null; then
        echo -e "${YELLOW}📦 Instalando pytest...${NC}"
        docker exec $API_CONTAINER pip install pytest pytest-cov pytest-asyncio pytest-mock
    else
        echo -e "${GREEN}✅ pytest ya está instalado${NC}"
    fi
}

# Función para ejecutar tests unitarios
run_unit_tests() {
    echo ""
    echo -e "${YELLOW}🔬 Ejecutando tests unitarios...${NC}"
    echo "================================="
    
    docker exec $API_CONTAINER python -m pytest /app/tests/ \
        -v \
        --tb=short \
        --durations=10 \
        --color=yes || true
}

# Función para ejecutar tests con cobertura
run_coverage_tests() {
    echo ""
    echo -e "${YELLOW}📊 Ejecutando tests con cobertura...${NC}"
    echo "====================================="
    
    docker exec $API_CONTAINER python -m pytest /app/tests/ \
        --cov=/app/src \
        --cov-report=term-missing \
        --cov-report=html:/app/testing/reports/coverage_html \
        --cov-fail-under=50 \
        --tb=short || true
}

# Función para ejecutar tests específicos de OCR
run_ocr_tests() {
    echo ""
    echo -e "${YELLOW}👁️ Ejecutando tests específicos de OCR...${NC}"
    echo "==========================================="
    
    # Test con PDF digital
    if [ -f "tests/fixtures/digital.pdf" ]; then
        echo -e "${BLUE}📄 Probando PDF digital...${NC}"
        docker exec $API_CONTAINER python -m pytest /app/tests/test_digital_pdfs.py -v || true
    fi
    
    # Test con PDF escaneado
    if [ -f "tests/fixtures/scanned.pdf" ]; then
        echo -e "${BLUE}📄 Probando PDF escaneado...${NC}"
        docker exec $API_CONTAINER python -m pytest /app/tests/test_scanned_pdfs.py -v || true
    fi
}

# Función para ejecutar tests de API
run_api_tests() {
    echo ""
    echo -e "${YELLOW}🌐 Ejecutando tests de API...${NC}"
    echo "=============================="
    
    # Verificar que la API esté funcionando
    echo -e "${BLUE}🔍 Verificando salud de la API...${NC}"
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ API está respondiendo${NC}"
        
        # Ejecutar tests de endpoints si existen
        docker exec $API_CONTAINER python -m pytest /app/tests/ -k "api" -v || true
    else
        echo -e "${YELLOW}⚠️ API no está disponible en localhost:8000${NC}"
    fi
}

# Función para ejecutar tests de rendimiento básicos
run_performance_tests() {
    echo ""
    echo -e "${YELLOW}⚡ Ejecutando tests de rendimiento básicos...${NC}"
    echo "=============================================="
    
    # Test de memoria y tiempo con un PDF pequeño
    if [ -f "tests/fixtures/digital.pdf" ]; then
        echo -e "${BLUE}📊 Midiendo rendimiento con PDF de prueba...${NC}"
        docker exec $API_CONTAINER python -c "
import time
import sys
import tracemalloc
from pathlib import Path

# Iniciar medición de memoria
tracemalloc.start()

try:
    # Importar el adaptador principal
    from adapters.out.ocr.pymupdf_adapter import PyMuPDFAdapter
    
    # Medir tiempo de procesamiento
    start_time = time.time()
    
    adapter = PyMuPDFAdapter()
    pdf_path = Path('tests/fixtures/digital.pdf')
    
    if pdf_path.exists():
        result = adapter.extract_text_and_metadata(pdf_path)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Medir memoria
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f'✅ Tiempo de procesamiento: {processing_time:.2f} segundos')
        print(f'📊 Memoria actual: {current / 1024 / 1024:.1f} MB')
        print(f'📈 Pico de memoria: {peak / 1024 / 1024:.1f} MB')
        print(f'📄 Páginas procesadas: {len(result[1]) if len(result) > 1 else 0}')
    else:
        print('⚠️ Archivo de prueba no encontrado')
        
except Exception as e:
    print(f'❌ Error en test de rendimiento: {e}')
" || true
    fi
}

# Función para generar reporte de tests
generate_test_report() {
    echo ""
    echo -e "${MAGENTA}📋 Generando reporte de tests...${NC}"
    echo "=================================="
    
    REPORT_FILE="testing/reports/test_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "REPORTE DE TESTS - OCR-PYMUPDF"
        echo "==============================="
        echo "Fecha: $(date)"
        echo "Commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'N/A')"
        echo ""
        echo "ARCHIVOS DE TEST ENCONTRADOS:"
        find tests -name "*.py" -type f | head -20
        echo ""
        echo "ESTADO DE CONTENEDORES:"
        docker ps --filter name=ocr-pymupdf
        echo ""
        echo "VERSIONES INSTALADAS:"
        docker exec $API_CONTAINER pip list | grep -E "(pytest|coverage|black|flake8|mypy)"
    } > "$REPORT_FILE"
    
    echo -e "${GREEN}✅ Reporte guardado en: $REPORT_FILE${NC}"
}

# Función principal
main() {
    # Procesar argumentos
    RUN_COVERAGE=false
    RUN_PERFORMANCE=false
    QUICK_MODE=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --coverage)
                RUN_COVERAGE=true
                shift
                ;;
            --performance)
                RUN_PERFORMANCE=true
                shift
                ;;
            --quick)
                QUICK_MODE=true
                shift
                ;;
            --help|-h)
                echo "Uso: $0 [opciones]"
                echo "Opciones:"
                echo "  --coverage      Ejecutar tests con cobertura de código"
                echo "  --performance   Incluir tests de rendimiento"
                echo "  --quick         Solo tests básicos y rápidos"
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
    install_pytest
    
    if [ "$QUICK_MODE" = true ]; then
        echo -e "${BLUE}⚡ Modo rápido: Solo tests esenciales${NC}"
        run_unit_tests
    else
        run_unit_tests
        run_ocr_tests
        run_api_tests
        
        if [ "$RUN_COVERAGE" = true ]; then
            run_coverage_tests
        fi
        
        if [ "$RUN_PERFORMANCE" = true ]; then
            run_performance_tests
        fi
    fi
    
    generate_test_report
    
    echo ""
    echo -e "${GREEN}✅ Tests completados${NC}"
    echo "💡 Tip: Usa --coverage para análisis de cobertura o --performance para tests de rendimiento"
}

# Ejecutar función principal con todos los argumentos
main "$@"
