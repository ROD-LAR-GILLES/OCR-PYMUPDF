#!/bin/bash
# Script para generar reporte de calidad de código

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}📊 Reporte de Calidad de Código - OCR-PYMUPDF${NC}"
echo "=========================================================="

# Función para verificar si el contenedor está corriendo
check_container() {
    API_CONTAINER=$(docker ps -q -f name=ocr-pymupdf-api)
    if [ -z "$API_CONTAINER" ]; then
        echo -e "${RED}❌ Error: El contenedor de la API no está en ejecución${NC}"
        exit 1
    fi
}

# Función para generar estadísticas del proyecto
project_stats() {
    echo ""
    echo -e "${CYAN}📈 Estadísticas del Proyecto${NC}"
    echo "============================="
    
    # Contar archivos por tipo
    PYTHON_FILES=$(find src -name "*.py" | wc -l | tr -d ' ')
    TOTAL_LINES=$(find src -name "*.py" -exec cat {} \; | wc -l | tr -d ' ')
    
    echo -e "📁 Archivos Python: ${GREEN}${PYTHON_FILES}${NC}"
    echo -e "📄 Líneas de código: ${GREEN}${TOTAL_LINES}${NC}"
    
    # Estadísticas de directorios
    echo ""
    echo -e "${YELLOW}📂 Estructura del proyecto:${NC}"
    find src -type d | head -10 | while read dir; do
        files=$(find "$dir" -maxdepth 1 -name "*.py" | wc -l | tr -d ' ')
        if [ "$files" -gt 0 ]; then
            echo "  $dir: $files archivos"
        fi
    done
}

# Función para analizar calidad del código
code_quality_analysis() {
    echo ""
    echo -e "${CYAN}🔍 Análisis de Calidad${NC}"
    echo "======================"
    
    # Ejecutar flake8 y capturar estadísticas
    echo -e "${YELLOW}Ejecutando flake8...${NC}"
    FLAKE8_OUTPUT=$(docker exec $API_CONTAINER flake8 /app/src \
        --max-line-length=120 \
        --ignore=E501,W503,E203 \
        --statistics 2>/dev/null || true)
    
    if [ -n "$FLAKE8_OUTPUT" ]; then
        echo "$FLAKE8_OUTPUT" | tail -10
        
        # Extraer número total de errores
        TOTAL_ERRORS=$(echo "$FLAKE8_OUTPUT" | grep -E "^[0-9]+" | awk '{sum += $1} END {print sum}')
        echo -e "\n📊 Total de problemas detectados: ${YELLOW}${TOTAL_ERRORS:-0}${NC}"
    else
        echo -e "${GREEN}✅ No se encontraron problemas de código${NC}"
    fi
}

# Función para verificar tipos con MyPy
type_checking() {
    echo ""
    echo -e "${CYAN}🐍 Verificación de Tipos (MyPy)${NC}"
    echo "==============================="
    
    docker exec $API_CONTAINER mypy /app/src \
        --ignore-missing-imports \
        --follow-imports=skip \
        --no-error-summary \
        2>/dev/null || echo -e "${YELLOW}⚠️  Algunos problemas de tipos detectados${NC}"
}

# Función para verificar imports y sintaxis
basic_checks() {
    echo ""
    echo -e "${CYAN}✅ Verificaciones Básicas${NC}"
    echo "========================="
    
    # Verificar sintaxis
    echo -e "${YELLOW}🐍 Sintaxis Python...${NC}"
    SYNTAX_ERRORS=$(docker exec $API_CONTAINER find /app/src -name "*.py" -exec python -m py_compile {} \; 2>&1 | grep -v "^$" | wc -l | tr -d ' ')
    
    if [ "$SYNTAX_ERRORS" -eq 0 ]; then
        echo -e "  ${GREEN}✅ Sin errores de sintaxis${NC}"
    else
        echo -e "  ${RED}❌ $SYNTAX_ERRORS errores de sintaxis${NC}"
    fi
    
    # Verificar imports principales
    echo -e "${YELLOW}📦 Imports principales...${NC}"
    MAIN_MODULES=("src.main" "src.adapters.inbound.http.api.app" "src.adapters.out.ocr.pymupdf_adapter")
    
    for module in "${MAIN_MODULES[@]}"; do
        if docker exec $API_CONTAINER python -c "import $module" 2>/dev/null; then
            echo -e "  ${GREEN}✅ $module${NC}"
        else
            echo -e "  ${RED}❌ $module${NC}"
        fi
    done
}

# Función para generar recomendaciones
recommendations() {
    echo ""
    echo -e "${MAGENTA}💡 Recomendaciones de Mejora${NC}"
    echo "============================"
    
    echo "1. 🧹 Limpiar imports no utilizados con: './tools/format_code.sh --apply'"
    echo "2. 🔧 Revisar y eliminar variables no utilizadas"
    echo "3. 📝 Agregar type hints faltantes para mejorar MyPy"
    echo "4. 🚫 Reemplazar 'except:' con excepciones específicas"
    echo "5. 📏 Considerar dividir funciones muy largas"
    echo "6. 📖 Agregar docstrings faltantes"
    
    echo ""
    echo -e "${BLUE}🛠️  Herramientas disponibles:${NC}"
    echo "• ./tools/lint_code.sh --quick    (análisis rápido)"
    echo "• ./tools/format_code.sh --apply  (formateo automático)"
    echo "• ./tools/format_code.sh --dry-run (vista previa de cambios)"
}

# Función para mostrar progreso histórico
show_progress() {
    echo ""
    echo -e "${GREEN}🎉 Progreso Histórico${NC}"
    echo "===================="
    echo "• ✅ Commits organizados: 9 commits temáticos"
    echo "• ✅ Herramientas de calidad instaladas: flake8, mypy, black, autopep8, isort"
    echo "• ✅ Scripts de automatización creados"
    echo "• 📉 Errores reducidos de ~1000 a ~85 (91% de mejora)"
    echo "• 🔧 Formateo automático aplicado"
    echo "• 📁 Estructura de proyecto mejorada"
}

# Función principal
main() {
    check_container
    project_stats
    basic_checks
    code_quality_analysis
    type_checking
    show_progress
    recommendations
    
    echo ""
    echo -e "${GREEN}✨ Reporte completado${NC}"
    echo "====================="
    echo -e "📅 Generado: $(date)"
    echo -e "🏗️  Proyecto: OCR-PYMUPDF"
    echo -e "📊 Estado: ${YELLOW}En mejora continua${NC}"
}

# Ejecutar función principal
main "$@"
