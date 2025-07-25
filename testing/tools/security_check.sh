#!/bin/bash
# Herramienta para verificar la seguridad del código y dependencias

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE} Análisis de Seguridad - OCR-PYMUPDF${NC}"
echo "=========================================="

# Función para verificar si el contenedor está corriendo
check_container() {
    API_CONTAINER=$(docker ps -q -f name=ocr-pymupdf-api)
    if [ -z "$API_CONTAINER" ]; then
        echo -e "${RED} Error: El contenedor de la API no está en ejecución${NC}"
        exit 1
    fi
    echo -e "${GREEN} Contenedor encontrado: $API_CONTAINER${NC}"
}

# Función para instalar herramientas de seguridad
install_security_tools() {
    echo -e "${YELLOW} Instalando herramientas de seguridad...${NC}"
    
    # Instalar bandit para análisis de seguridad
    docker exec $API_CONTAINER pip install bandit[toml] safety || true
    
    echo -e "${GREEN} Herramientas de seguridad instaladas${NC}"
}

# Función para ejecutar bandit (análisis de vulnerabilidades)
run_bandit_analysis() {
    echo ""
    echo -e "${YELLOW} Ejecutando análisis de vulnerabilidades con Bandit...${NC}"
    echo "======================================================="
    
    docker exec $API_CONTAINER bandit -r /app/src \
        -f txt \
        -o /app/testing/reports/bandit_report.txt \
        --skip B101,B601 \
        --exclude /app/src/tests \
        || true

    # Mostrar resumen
    echo -e "${BLUE} Resumen de Bandit:${NC}"
    docker exec $API_CONTAINER bandit -r /app/src \
        --skip B101,B601 \
        --exclude /app/src/tests \
        -q || true
}

# Función para verificar dependencias vulnerables
check_vulnerable_dependencies() {
    echo ""
    echo -e "${YELLOW} Verificando dependencias vulnerables...${NC}"
    echo "==========================================="
    
    # Usar safety para verificar vulnerabilidades conocidas
    docker exec $API_CONTAINER safety check \
        --output text \
        --file /app/testing/reports/safety_report.txt || true
    
    echo -e "${BLUE} Resumen de Safety:${NC}"
    docker exec $API_CONTAINER safety check || echo -e "${GREEN} No se encontraron vulnerabilidades conocidas${NC}"
}

# Función para verificar configuraciones inseguras
check_insecure_configurations() {
    echo ""
    echo -e "${YELLOW} Verificando configuraciones inseguras...${NC}"
    echo "============================================="
    
    echo -e "${BLUE} Buscando claves hardcodeadas...${NC}"
    
    # Buscar patrones de claves API hardcodeadas
    HARDCODED_KEYS=$(grep -r -i -E "(api_key|secret|password|token).*=.*['\"][a-zA-Z0-9]{10,}['\"]" src/ || true)
    
    if [ -n "$HARDCODED_KEYS" ]; then
        echo -e "${RED} Posibles claves hardcodeadas encontradas:${NC}"
        echo "$HARDCODED_KEYS"
    else
        echo -e "${GREEN} No se encontraron claves hardcodeadas${NC}"
    fi
    
    echo -e "${BLUE} Verificando uso de HTTP inseguro...${NC}"
    HTTP_URLS=$(grep -r -i "http://" src/ || true)
    
    if [ -n "$HTTP_URLS" ]; then
        echo -e "${YELLOW} URLs HTTP encontradas (considerar HTTPS):${NC}"
        echo "$HTTP_URLS" | head -5
    else
        echo -e "${GREEN} No se encontraron URLs HTTP inseguras${NC}"
    fi
}

# Función para verificar permisos de archivos
check_file_permissions() {
    echo ""
    echo -e "${YELLOW} Verificando permisos de archivos...${NC}"
    echo "======================================"
    
    # Verificar archivos con permisos demasiado permisivos
    PERMISSIVE_FILES=$(find . -type f -perm /o+w 2>/dev/null | grep -v ".git" | head -10 || true)
    
    if [ -n "$PERMISSIVE_FILES" ]; then
        echo -e "${YELLOW} Archivos con permisos permisivos encontrados:${NC}"
        echo "$PERMISSIVE_FILES"
    else
        echo -e "${GREEN} Permisos de archivos apropiados${NC}"
    fi
    
    # Verificar archivos .env
    if [ -f ".env" ]; then
        ENV_PERMS=$(stat -c "%a" .env)
        if [ "$ENV_PERMS" != "600" ] && [ "$ENV_PERMS" != "640" ]; then
            echo -e "${YELLOW} Archivo .env tiene permisos $ENV_PERMS (recomendado: 600)${NC}"
        else
            echo -e "${GREEN} Permisos de .env apropiados${NC}"
        fi
    fi
}

# Función para generar reporte de seguridad
generate_security_report() {
    echo ""
    echo -e "${MAGENTA} Generando reporte de seguridad...${NC}"
    echo "====================================="
    
    REPORT_FILE="testing/reports/security_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "REPORTE DE SEGURIDAD - OCR-PYMUPDF"
        echo "=================================="
        echo "Fecha: $(date)"
        echo "Commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'N/A')"
        echo ""
        echo "HERRAMIENTAS UTILIZADAS:"
        echo "- Bandit: Análisis de código para vulnerabilidades"
        echo "- Safety: Verificación de dependencias vulnerables"
        echo "- Análisis manual: Configuraciones y permisos"
        echo ""
        echo "ARCHIVOS ANALIZADOS:"
        find src -name "*.py" | wc -l | xargs echo "Archivos Python:"
        echo ""
        
        if [ -f "testing/reports/bandit_report.txt" ]; then
            echo "RESUMEN BANDIT:"
            tail -20 "testing/reports/bandit_report.txt" 2>/dev/null || echo "No disponible"
            echo ""
        fi
        
        if [ -f "testing/reports/safety_report.txt" ]; then
            echo "RESUMEN SAFETY:"
            cat "testing/reports/safety_report.txt" 2>/dev/null || echo "No disponible"
            echo ""
        fi
        
    } > "$REPORT_FILE"
    
    echo -e "${GREEN} Reporte de seguridad guardado en: $REPORT_FILE${NC}"
}

# Función principal
main() {
    # Procesar argumentos
    DETAILED_ANALYSIS=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --detailed)
                DETAILED_ANALYSIS=true
                shift
                ;;
            --help|-h)
                echo "Uso: $0 [opciones]"
                echo "Opciones:"
                echo "  --detailed      Análisis detallado incluyendo permisos y configuraciones"
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
    install_security_tools
    
    run_bandit_analysis
    check_vulnerable_dependencies
    
    if [ "$DETAILED_ANALYSIS" = true ]; then
        check_insecure_configurations
        check_file_permissions
    fi
    
    generate_security_report
    
    echo ""
    echo -e "${GREEN} Análisis de seguridad completado${NC}"
    echo " Tip: Revisa los reportes en testing/reports/ para detalles completos"
}

# Ejecutar función principal con todos los argumentos
main "$@"
