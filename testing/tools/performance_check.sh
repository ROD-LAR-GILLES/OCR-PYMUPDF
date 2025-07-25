#!/bin/bash
# Herramienta para verificar rendimiento y recursos del sistema

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}⚡ Análisis de Rendimiento - OCR-PYMUPDF${NC}"
echo "============================================"

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

# Función para verificar recursos del sistema
check_system_resources() {
    echo ""
    echo -e "${CYAN}🖥️ Recursos del Sistema${NC}"
    echo "======================="
    
    echo -e "${YELLOW}📊 Uso de CPU y Memoria del contenedor:${NC}"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" ocr-pymupdf-api || true
    
    echo -e "${YELLOW}💾 Espacio en disco:${NC}"
    df -h . | tail -1 | awk '{print "Disponible: " $4 " de " $2 " (" $5 " usado)"}'
    
    echo -e "${YELLOW}🐳 Imágenes Docker:${NC}"
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep -E "(ocr-pymupdf|python|nginx)" || true
}

# Función para medir tiempo de inicio
measure_startup_time() {
    echo ""
    echo -e "${CYAN}🚀 Tiempo de Inicio${NC}"
    echo "==================="
    
    echo -e "${YELLOW}📈 Midiendo tiempo de inicio del contenedor...${NC}"
    
    # Parar contenedor si está corriendo
    docker-compose down >/dev/null 2>&1 || true
    
    # Medir tiempo de inicio
    START_TIME=$(date +%s)
    docker-compose up -d >/dev/null 2>&1
    
    # Esperar hasta que la API responda
    echo -e "${BLUE}⏳ Esperando que la API esté lista...${NC}"
    TIMEOUT=60
    ELAPSED=0
    
    while [ $ELAPSED -lt $TIMEOUT ]; do
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            END_TIME=$(date +%s)
            STARTUP_TIME=$((END_TIME - START_TIME))
            echo -e "${GREEN}✅ API lista en $STARTUP_TIME segundos${NC}"
            break
        fi
        sleep 2
        ELAPSED=$((ELAPSED + 2))
    done
    
    if [ $ELAPSED -ge $TIMEOUT ]; then
        echo -e "${RED}❌ Timeout: API no respondió en $TIMEOUT segundos${NC}"
    fi
}

# Función para medir rendimiento de OCR
measure_ocr_performance() {
    echo ""
    echo -e "${CYAN}👁️ Rendimiento de OCR${NC}"
    echo "====================="
    
    echo -e "${YELLOW}📄 Procesando PDFs de prueba...${NC}"
    
    # Crear script de benchmark dentro del contenedor
    docker exec $API_CONTAINER python -c "
import time
import tracemalloc
from pathlib import Path
import sys

def benchmark_pdf(pdf_path, description):
    print(f'📊 Analizando {description}...')
    
    if not pdf_path.exists():
        print(f'⚠️ {pdf_path} no encontrado')
        return None
    
    # Iniciar medición
    tracemalloc.start()
    start_time = time.time()
    
    try:
        from adapters.out.ocr.pymupdf_adapter import PyMuPDFAdapter
        adapter = PyMuPDFAdapter()
        
        # Procesar PDF
        result = adapter.extract_text_and_metadata(pdf_path)
        
        # Finalizar medición
        end_time = time.time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        processing_time = end_time - start_time
        pages = len(result[1]) if len(result) > 1 else 0
        
        print(f'  ⏱️ Tiempo: {processing_time:.2f}s')
        print(f'  📄 Páginas: {pages}')
        print(f'  💾 Memoria pico: {peak / 1024 / 1024:.1f} MB')
        print(f'  📊 Velocidad: {pages/processing_time:.1f} páginas/segundo')
        print()
        
        return {
            'time': processing_time,
            'pages': pages,
            'memory_peak': peak,
            'speed': pages/processing_time if processing_time > 0 else 0
        }
        
    except Exception as e:
        print(f'  ❌ Error: {e}')
        return None

# Ejecutar benchmarks
test_files = [
    (Path('tests/fixtures/digital.pdf'), 'PDF Digital'),
    (Path('tests/fixtures/scanned.pdf'), 'PDF Escaneado'),
    (Path('pdfs/pdf_scan.pdf'), 'PDF Muestra')
]

results = []
for pdf_path, description in test_files:
    result = benchmark_pdf(pdf_path, description)
    if result:
        results.append((description, result))

# Mostrar resumen
if results:
    print('📈 RESUMEN DE RENDIMIENTO:')
    print('========================')
    for desc, result in results:
        print(f'{desc}:')
        print(f'  - Tiempo: {result[\"time\"]:.2f}s')
        print(f'  - Velocidad: {result[\"speed\"]:.1f} pág/s')
        print(f'  - Memoria: {result[\"memory_peak\"] / 1024 / 1024:.1f} MB')
else:
    print('⚠️ No se pudieron procesar archivos de prueba')
" || echo -e "${YELLOW}⚠️ Error en benchmark de OCR${NC}"
}

# Función para medir rendimiento de API
measure_api_performance() {
    echo ""
    echo -e "${CYAN}🌐 Rendimiento de API${NC}"
    echo "====================="
    
    if ! curl -f http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️ API no está disponible, saltando tests de API${NC}"
        return
    fi
    
    echo -e "${YELLOW}📡 Midiendo latencia de endpoints...${NC}"
    
    # Test de endpoint de salud
    echo -e "${BLUE}🔍 GET /health${NC}"
    time curl -s http://localhost:8000/health >/dev/null || echo "Error"
    
    echo -e "${BLUE}🔍 GET /api/health${NC}"
    time curl -s http://localhost:8000/api/health >/dev/null || echo "Error"
    
    # Test de carga básico si hay curl disponible
    if command -v ab >/dev/null 2>&1; then
        echo -e "${YELLOW}🔥 Test de carga básico (Apache Bench)...${NC}"
        ab -n 50 -c 5 http://localhost:8000/health 2>/dev/null | grep -E "(Requests per second|Time per request)" || echo "Apache Bench no disponible"
    fi
}

# Función para verificar uso de memoria en el tiempo
monitor_memory_usage() {
    echo ""
    echo -e "${CYAN}📊 Monitoreo de Memoria${NC}"
    echo "======================="
    
    echo -e "${YELLOW}📈 Monitoreando uso de memoria por 30 segundos...${NC}"
    
    for i in {1..10}; do
        MEMORY_USAGE=$(docker stats --no-stream --format "{{.MemUsage}}" ocr-pymupdf-api 2>/dev/null || echo "N/A")
        CPU_USAGE=$(docker stats --no-stream --format "{{.CPUPerc}}" ocr-pymupdf-api 2>/dev/null || echo "N/A")
        echo "[$i/10] CPU: $CPU_USAGE | Memory: $MEMORY_USAGE"
        sleep 3
    done
}

# Función para generar reporte de rendimiento
generate_performance_report() {
    echo ""
    echo -e "${MAGENTA}📋 Generando reporte de rendimiento...${NC}"
    echo "======================================"
    
    REPORT_FILE="testing/reports/performance_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "REPORTE DE RENDIMIENTO - OCR-PYMUPDF"
        echo "===================================="
        echo "Fecha: $(date)"
        echo "Commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'N/A')"
        echo ""
        echo "INFORMACIÓN DEL SISTEMA:"
        echo "- OS: $(uname -s)"
        echo "- Arquitectura: $(uname -m)"
        echo "- Docker version: $(docker --version 2>/dev/null || echo 'N/A')"
        echo ""
        echo "RECURSOS DEL CONTENEDOR:"
        docker stats --no-stream --format "{{.Name}}: CPU {{.CPUPerc}} | Memory {{.MemUsage}} ({{.MemPerc}})" ocr-pymupdf-api 2>/dev/null || echo "N/A"
        echo ""
        echo "ARCHIVOS DE PRUEBA DISPONIBLES:"
        find tests/fixtures -name "*.pdf" 2>/dev/null || echo "No encontrados"
        find pdfs -name "*.pdf" 2>/dev/null | head -3 || echo "No encontrados"
        
    } > "$REPORT_FILE"
    
    echo -e "${GREEN}✅ Reporte de rendimiento guardado en: $REPORT_FILE${NC}"
}

# Función principal
main() {
    # Procesar argumentos
    FULL_BENCHMARK=false
    MONITOR_MEMORY=false
    STARTUP_TEST=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --full)
                FULL_BENCHMARK=true
                shift
                ;;
            --monitor)
                MONITOR_MEMORY=true
                shift
                ;;
            --startup)
                STARTUP_TEST=true
                shift
                ;;
            --help|-h)
                echo "Uso: $0 [opciones]"
                echo "Opciones:"
                echo "  --full          Benchmark completo incluyendo OCR y API"
                echo "  --monitor       Monitorear uso de memoria en tiempo real"
                echo "  --startup       Medir tiempo de inicio del contenedor"
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
    check_system_resources
    
    if [ "$STARTUP_TEST" = true ]; then
        measure_startup_time
    fi
    
    if [ "$FULL_BENCHMARK" = true ]; then
        measure_ocr_performance
        measure_api_performance
    fi
    
    if [ "$MONITOR_MEMORY" = true ]; then
        monitor_memory_usage
    fi
    
    generate_performance_report
    
    echo ""
    echo -e "${GREEN}⚡ Análisis de rendimiento completado${NC}"
    echo "💡 Tip: Usa --full para benchmark completo o --monitor para monitoreo en tiempo real"
}

# Ejecutar función principal con todos los argumentos
main "$@"
