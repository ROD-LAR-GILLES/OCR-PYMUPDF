#!/bin/bash
# Script de mantenimiento de código para el proyecto OCR-PYMUPDF
# Incluye limpieza de emoticones, formateo y análisis de calidad

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo -e "${BLUE}  Herramienta de Mantenimiento de Código - OCR-PYMUPDF${NC}"
echo "============================================================="

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [OPCION]"
    echo ""
    echo "Opciones:"
    echo "  --clean-emojis    Eliminar emoticones de todos los archivos"
    echo "  --check-emojis    Verificar si hay emoticones (sin modificar)"
    echo "  --format          Formatear código con black e isort"
    echo "  --lint            Ejecutar análisis de calidad"
    echo "  --full            Ejecutar mantenimiento completo"
    echo "  --help, -h        Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 --clean-emojis  # Limpiar emoticones"
    echo "  $0 --full          # Mantenimiento completo"
    echo ""
}

# Función para limpiar emoticones
clean_emojis() {
    echo ""
    echo -e "${CYAN}  Limpiando emoticones del proyecto...${NC}"
    echo "========================================"
    
    if [ ! -f "$SCRIPT_DIR/clean_emojis.py" ]; then
        echo -e "${RED}  Error: No se encontró el script clean_emojis.py${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Ejecutando limpieza de emoticones...${NC}"
    
    cd "$PROJECT_ROOT"
    python3 "$SCRIPT_DIR/clean_emojis.py" --verbose
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}  Limpieza de emoticones completada${NC}"
    else
        echo -e "${RED}  Error durante la limpieza de emoticones${NC}"
        return 1
    fi
}

# Función para verificar emoticones
check_emojis() {
    echo ""
    echo -e "${CYAN}  Verificando emoticones en el proyecto...${NC}"
    echo "==========================================="
    
    if [ ! -f "$SCRIPT_DIR/clean_emojis.py" ]; then
        echo -e "${RED}  Error: No se encontró el script clean_emojis.py${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Buscando emoticones...${NC}"
    
    cd "$PROJECT_ROOT"
    python3 "$SCRIPT_DIR/clean_emojis.py" --dry-run --verbose
    
    echo -e "${BLUE}  Para limpiar emoticones use: $0 --clean-emojis${NC}"
}

# Función para formatear código
format_code() {
    echo ""
    echo -e "${CYAN}  Formateando código...${NC}"
    echo "========================"
    
    if [ -f "$SCRIPT_DIR/format_code.sh" ]; then
        echo -e "${YELLOW}Ejecutando formateo automático...${NC}"
        bash "$SCRIPT_DIR/format_code.sh" --apply
    else
        echo -e "${YELLOW}Script de formateo no encontrado, usando comandos básicos...${NC}"
        
        # Formateo básico con black si está disponible
        if command -v black > /dev/null 2>&1; then
            echo "Ejecutando black..."
            cd "$PROJECT_ROOT"
            black src/ tests/ --line-length=120 --quiet || true
        fi
        
        # Organizar imports con isort si está disponible
        if command -v isort > /dev/null 2>&1; then
            echo "Organizando imports..."
            cd "$PROJECT_ROOT"
            isort src/ tests/ --profile=black --quiet || true
        fi
    fi
    
    echo -e "${GREEN}  Formateo completado${NC}"
}

# Función para análisis de calidad
lint_code() {
    echo ""
    echo -e "${CYAN}  Ejecutando análisis de calidad...${NC}"
    echo "===================================="
    
    if [ -f "$SCRIPT_DIR/lint_code.sh" ]; then
        echo -e "${YELLOW}Ejecutando análisis completo...${NC}"
        bash "$SCRIPT_DIR/lint_code.sh" --quick
    else
        echo -e "${YELLOW}Script de análisis no encontrado, usando comandos básicos...${NC}"
        
        # Análisis básico con flake8 si está disponible
        if command -v flake8 > /dev/null 2>&1; then
            echo "Ejecutando flake8..."
            cd "$PROJECT_ROOT"
            flake8 src/ --max-line-length=120 --count --statistics || true
        fi
    fi
    
    echo -e "${GREEN}  Análisis completado${NC}"
}

# Función para mantenimiento completo
full_maintenance() {
    echo ""
    echo -e "${MAGENTA}  Ejecutando mantenimiento completo...${NC}"
    echo "========================================"
    
    # 1. Verificar emoticones primero
    check_emojis
    
    # 2. Limpiar emoticones si se encontraron
    clean_emojis
    
    # 3. Formatear código
    format_code
    
    # 4. Análisis de calidad
    lint_code
    
    echo ""
    echo -e "${GREEN}  Mantenimiento completo finalizado${NC}"
    echo "===================================="
    echo ""
    echo -e "${BLUE}Resumen de acciones realizadas:${NC}"
    echo "•   Limpieza de emoticones"
    echo "•   Formateo de código"
    echo "•   Análisis de calidad"
    echo ""
    echo -e "${YELLOW}  Recomendaciones:${NC}"
    echo "• Revisar y confirmar cambios antes de hacer commit"
    echo "• Ejecutar tests para verificar que todo funciona"
    echo "• Considerar agregar este script a los hooks de git"
}

# Función principal
main() {
    case "${1:-}" in
        --clean-emojis)
            clean_emojis
            ;;
        --check-emojis)
            check_emojis
            ;;
        --format)
            format_code
            ;;
        --lint)
            lint_code
            ;;
        --full)
            full_maintenance
            ;;
        --help|-h)
            show_help
            ;;
        "")
            echo -e "${YELLOW} ️  No se especificó ninguna opción${NC}"
            echo ""
            show_help
            exit 1
            ;;
        *)
            echo -e "${RED}  Opción desconocida: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Ejecutar función principal con todos los argumentos
main "$@"
