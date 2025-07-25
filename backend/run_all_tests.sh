#!/bin/bash
# MASTER TESTING SCRIPT - Ejecuta todas las herramientas de testing y calidad
# Este script es tu punto de entrada único para verificar todo el proyecto

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Banner principal
echo -e "${BOLD}${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                      MASTER TESTING SUITE - OCR-PYMUPDF                      ║"
echo "║                                                                              ║"
echo "║    Tests Unitarios  │    Análisis de Código  │    Seguridad                  ║"
echo "║    Rendimiento      │    Calidad             │    Reportes                   ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Variables globales
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
TOOLS_DIR="$PROJECT_ROOT/tools"
REPORTS_DIR="$PROJECT_ROOT/tools/reports"

# Crear directorios si no existen
mkdir -p "$REPORTS_DIR"

# Función para mostrar ayuda
show_help() {
    echo -e "${CYAN} GUÍA DE USO${NC}"
    echo "=============="
    echo ""
    echo -e "${BOLD}./run_all_tests.sh [opciones]${NC}"
    echo ""
    echo -e "${YELLOW}  MODOS PREDEFINIDOS:${NC}"
    echo "  --quick           Verificación rápida (5-10 min)"
    echo "  --standard        Análisis estándar (15-20 min)"
    echo "  --full            Análisis completo (30+ min)"
    echo "  --ci              Modo CI/CD (solo errores críticos)"
    echo ""
    echo -e "${YELLOW}  OPCIONES ESPECÍFICAS:${NC}"
    echo "  --tests           Solo ejecutar tests unitarios"
    echo "  --quality         Solo análisis de calidad de código"
    echo "  --security        Solo verificación de seguridad"
    echo "  --performance     Solo análisis de rendimiento"
    echo "  --format          Solo formateo de código"
    echo "  --clean-emojis    Solo limpieza de emoticones"
    echo ""
    echo -e "${YELLOW}  MODIFICADORES:${NC}"
    echo "  --coverage        Incluir análisis de cobertura"
    echo "  --verbose         Output detallado"
    echo "  --no-reports      No generar reportes"
    echo "  --parallel        Ejecutar en paralelo cuando sea posible"
    echo ""
    echo -e "${YELLOW}  EJEMPLOS:${NC}"
    echo "  ./run_all_tests.sh --quick --verbose"
    echo "  ./run_all_tests.sh --full --coverage"
    echo "  ./run_all_tests.sh --tests --security"
    echo "  ./run_all_tests.sh --ci"
    echo ""
    exit 0
}

# Función para verificar prerrequisitos
check_prerequisites() {
    echo -e "${BLUE}  Verificando prerrequisitos...${NC}"
    
    # Verificar que estamos en el directorio correcto
    if [ ! -f "docker-compose.yml" ] || [ ! -d "src" ]; then
        echo -e "${RED}  Error: Ejecuta este script desde la raíz del proyecto OCR-PYMUPDF${NC}"
        exit 1
    fi
    
    # Verificar Docker
    if ! command -v docker >/dev/null 2>&1; then
        echo -e "${RED}  Error: Docker no está instalado${NC}"
        exit 1
    fi
    
    # Verificar docker-compose
    if ! command -v docker-compose >/dev/null 2>&1; then
        echo -e "${RED}  Error: docker-compose no está instalado${NC}"
        exit 1
    fi
    
    # Verificar que las herramientas existen
    REQUIRED_TOOLS=(
        "$TOOLS_DIR/quality/lint_code.sh"
        "$TOOLS_DIR/maintenance/format_code.sh"
        "$TOOLS_DIR/quality/quality_report.sh"
        "$TOOLS_DIR/tests/run_tests.sh"
        "$TOOLS_DIR/security/security_check.sh"
        "$TOOLS_DIR/performance/performance_check.sh"
    )
    
    for tool in "${REQUIRED_TOOLS[@]}"; do
        if [ ! -f "$tool" ]; then
            echo -e "${RED}  Error: Herramienta faltante: $tool${NC}"
            exit 1
        fi
        chmod +x "$tool"
    done
    
    echo -e "${GREEN}  Prerrequisitos verificados${NC}"
}

# Función para inicializar el reporte maestro
init_master_report() {
    cat > "$MASTER_REPORT" << EOF
╔══════════════════════════════════════════════════════════════════════════════╗
║                      REPORTE MAESTRO - OCR-PYMUPDF                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

   Fecha: $(date)
   Session ID: $SESSION_ID
   Proyecto: OCR-PYMUPDF
   Commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'N/A')
   Rama: $(git branch --show-current 2>/dev/null || echo 'N/A')

═══════════════════════════════════════════════════════════════════════════════
  RESUMEN EJECUTIVO
═══════════════════════════════════════════════════════════════════════════════

EOF
}

# Función para ejecutar herramienta con logging
run_tool() {
    local tool_name="$1"
    local tool_script="$2"
    local tool_args="$3"
    local description="$4"
    
    echo ""
    echo -e "${BOLD}${CYAN}▶ $description${NC}"
    echo "$(printf '═%.0s' {1..80})"
    
    local start_time=$(date +%s)
    local success=true
    
    # Ejecutar herramienta y capturar output
    if [ "$VERBOSE" = true ]; then
        $tool_script $tool_args || success=false
    else
        $tool_script $tool_args >/dev/null 2>&1 || success=false
    fi
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Registrar resultado
    if [ "$success" = true ]; then
        echo -e "${GREEN}  $tool_name completado en ${duration}s${NC}"
        echo "  $tool_name - Completado en ${duration}s" >> "$MASTER_REPORT"
    else
        echo -e "${RED}  $tool_name falló después de ${duration}s${NC}"
        echo "  $tool_name - FALLÓ después de ${duration}s" >> "$MASTER_REPORT"
    fi
}

# Función para ejecutar formateo de código
run_code_formatting() {
    if [ "$RUN_FORMAT" = true ]; then
        run_tool "FORMAT" "$TOOLS_DIR/maintenance/format_code.sh" "--apply" "  Formateando código automáticamente"
    fi
}

# Función para ejecutar limpieza de emoticones
run_emoji_cleanup() {
    if [ "$RUN_CLEAN_EMOJIS" = true ]; then
        run_tool "EMOJIS" "python3 $TOOLS_DIR/maintenance/clean_emojis.py" "" "  Limpiando emoticones del proyecto"
    fi
}

# Función para ejecutar análisis de calidad
run_quality_analysis() {
    if [ "$RUN_QUALITY" = true ]; then
        run_tool "LINT" "$TOOLS_DIR/quality/lint_code.sh" "$LINT_ARGS" "  Analizando calidad de código"
        run_tool "QUALITY" "$TOOLS_DIR/quality/quality_report.sh" "" "  Generando reporte de calidad"
    fi
}

# Función para ejecutar tests
run_testing() {
    if [ "$RUN_TESTS" = true ]; then
        local test_args=""
        [ "$RUN_COVERAGE" = true ] && test_args="$test_args --coverage"
        [ "$QUICK_MODE" = true ] && test_args="$test_args --quick"
        
        run_tool "TESTS" "$TOOLS_DIR/tests/run_tests.sh" "$test_args" "  Ejecutando tests unitarios"
    fi
}

# Función para ejecutar análisis de seguridad
run_security_analysis() {
    if [ "$RUN_SECURITY" = true ]; then
        local security_args=""
        [ "$DETAILED_SECURITY" = true ] && security_args="--detailed"
        
        run_tool "SECURITY" "$TOOLS_DIR/security/security_check.sh" "$security_args" "  Verificando seguridad"
    fi
}

# Función para ejecutar análisis de rendimiento
run_performance_analysis() {
    if [ "$RUN_PERFORMANCE" = true ]; then
        local perf_args=""
        [ "$FULL_PERFORMANCE" = true ] && perf_args="--full"
        
        run_tool "PERFORMANCE" "$TOOLS_DIR/performance/performance_check.sh" "$perf_args" "  Analizando rendimiento"
    fi
}

# Función para finalizar reporte maestro
finalize_master_report() {
    if [ "$GENERATE_REPORTS" = true ]; then
        cat >> "$MASTER_REPORT" << EOF

═══════════════════════════════════════════════════════════════════════════════
  ARCHIVOS GENERADOS
═══════════════════════════════════════════════════════════════════════════════

Reportes disponibles en: $REPORTS_DIR/
$(ls -la "$REPORTS_DIR/" 2>/dev/null | grep "$(date +%Y%m%d)" || echo "No hay reportes del día de hoy")

═══════════════════════════════════════════════════════════════════════════════
  PRÓXIMOS PASOS RECOMENDADOS
═══════════════════════════════════════════════════════════════════════════════

1.   Revisar reportes detallados en tools/reports/
2.   Corregir problemas encontrados en análisis de calidad
3.   Agregar tests para código sin cobertura
4.   Resolver vulnerabilidades de seguridad si las hay
5.   Optimizar áreas de bajo rendimiento identificadas

═══════════════════════════════════════════════════════════════════════════════
  SOPORTE
═══════════════════════════════════════════════════════════════════════════════

Para más información sobre las herramientas:
• ./tools/quality/lint_code.sh --help
• ./tools/maintenance/format_code.sh --help
• ./tools/tests/run_tests.sh --help
• ./tools/maintenance/code_maintenance.sh --help
• ./tools/maintenance/clean_emojis.py --help

Documentación del proyecto: README.md
EOF
        
        echo ""
        echo -e "${MAGENTA}  Reporte maestro guardado en: $MASTER_REPORT${NC}"
    fi
}

# Función para mostrar resumen final
show_final_summary() {
    echo ""
    echo -e "${BOLD}${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                              TESTING COMPLETADO                              ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${CYAN}  RESUMEN DE LA SESIÓN:${NC}"
    echo "Session ID: $SESSION_ID"
    echo "Duración total: $(($(date +%s) - START_TIME)) segundos"
    echo ""
    
    if [ "$GENERATE_REPORTS" = true ]; then
        echo -e "${YELLOW}  REPORTES GENERADOS:${NC}"
        ls -la "$REPORTS_DIR/" | grep "$SESSION_ID" | while read line; do
            echo "  $line"
        done
    fi
    
    echo ""
    echo -e "${GREEN}  ¡Todas las verificaciones completadas!${NC}"
    echo -e "${BLUE}  Revisa los reportes en $REPORTS_DIR/ para detalles completos${NC}"
}

# Función principal
main() {
    # Variables por defecto
    QUICK_MODE=false
    STANDARD_MODE=false
    FULL_MODE=false
    CI_MODE=false
    
    RUN_TESTS=false
    RUN_QUALITY=false
    RUN_SECURITY=false
    RUN_PERFORMANCE=false
    RUN_FORMAT=false
    RUN_CLEAN_EMOJIS=false
    
    RUN_COVERAGE=false
    VERBOSE=false
    GENERATE_REPORTS=true
    PARALLEL=false
    
    DETAILED_SECURITY=false
    FULL_PERFORMANCE=false
    LINT_ARGS=""
    
    START_TIME=$(date +%s)
    SESSION_ID=$(date +%Y%m%d_%H%M%S)
    MASTER_REPORT="$REPORTS_DIR/master_report_${SESSION_ID}.txt"
    
    # Procesar argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            --quick)
                QUICK_MODE=true
                RUN_TESTS=true
                RUN_QUALITY=true
                LINT_ARGS="--quick"
                shift
                ;;
            --standard)
                STANDARD_MODE=true
                RUN_TESTS=true
                RUN_QUALITY=true
                RUN_SECURITY=true
                shift
                ;;
            --full)
                FULL_MODE=true
                RUN_TESTS=true
                RUN_QUALITY=true
                RUN_SECURITY=true
                RUN_PERFORMANCE=true
                RUN_COVERAGE=true
                DETAILED_SECURITY=true
                FULL_PERFORMANCE=true
                shift
                ;;
            --ci)
                CI_MODE=true
                RUN_TESTS=true
                RUN_QUALITY=true
                RUN_SECURITY=true
                LINT_ARGS="--quick"
                VERBOSE=false
                shift
                ;;
            --tests)
                RUN_TESTS=true
                shift
                ;;
            --quality)
                RUN_QUALITY=true
                shift
                ;;
            --security)
                RUN_SECURITY=true
                shift
                ;;
            --performance)
                RUN_PERFORMANCE=true
                shift
                ;;
            --format)
                RUN_FORMAT=true
                shift
                ;;
            --clean-emojis)
                RUN_CLEAN_EMOJIS=true
                shift
                ;;
            --coverage)
                RUN_COVERAGE=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --no-reports)
                GENERATE_REPORTS=false
                shift
                ;;
            --parallel)
                PARALLEL=true
                shift
                ;;
            --help|-h)
                show_help
                ;;
            *)
                echo "Opción desconocida: $1"
                echo "Usa --help para ver las opciones disponibles"
                exit 1
                ;;
        esac
    done
    
    # Si no se especifica nada, usar modo estándar
    if [ "$RUN_TESTS" = false ] && [ "$RUN_QUALITY" = false ] && [ "$RUN_SECURITY" = false ] && [ "$RUN_PERFORMANCE" = false ] && [ "$RUN_FORMAT" = false ] && [ "$RUN_CLEAN_EMOJIS" = false ]; then
        echo -e "${YELLOW}  No se especificaron opciones, usando modo estándar${NC}"
        STANDARD_MODE=true
        RUN_TESTS=true
        RUN_QUALITY=true
        RUN_SECURITY=true
    fi
    
    # Verificar prerrequisitos
    check_prerequisites
    
    # Crear directorio de reportes si no existe
    mkdir -p "$REPORTS_DIR"
    
    # Inicializar reporte maestro
    if [ "$GENERATE_REPORTS" = true ]; then
        init_master_report
    fi
    
    # Ejecutar herramientas en orden
    run_code_formatting
    run_emoji_cleanup
    run_testing
    run_quality_analysis
    run_security_analysis
    run_performance_analysis
    
    # Finalizar reporte
    if [ "$GENERATE_REPORTS" = true ]; then
        finalize_master_report
    fi
    
    # Mostrar resumen
    show_final_summary
}

# Ejecutar función principal con todos los argumentos
main "$@"
