#!/bin/bash

# Script principal para la reorganización del proyecto OCR-PYMUPDF
# Este script guía al usuario a través del proceso completo de reorganización

echo "=================================================================="
echo "      REORGANIZACIÓN DEL PROYECTO OCR-PYMUPDF"
echo "=================================================================="
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
echo "IMPORTANTE: Se recomienda hacer un respaldo del proyecto antes de continuar."
echo ""

read -p "¿Desea continuar con la reorganización? (s/n): " respuesta
if [[ "$respuesta" != "s" && "$respuesta" != "S" ]]; then
    echo "Reorganización cancelada."
    exit 0
fi

echo ""
echo "=== ETAPA 1: Creación de la nueva estructura de directorios ==="
echo ""

mkdir -p .config/flake8 .config/mypy .config/pytest .config/tox .config/pre-commit \
       docs/api docs/user docs/developer \
       scripts/data scripts/deployment scripts/maintenance \
       data/dictionaries data/corrections data/config \
       requirements bin

echo "Estructura de directorios creada con éxito."

echo ""
echo "=== ETAPA 2: Copia de archivos a sus nuevas ubicaciones ==="
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

echo "Archivos copiados a sus nuevas ubicaciones con éxito."

echo ""
echo "=== ETAPA 3: Actualización de referencias en el código ==="
echo ""

read -p "¿Desea actualizar las referencias en el código? (s/n): " respuesta
if [[ "$respuesta" == "s" || "$respuesta" == "S" ]]; then
    bash scripts/maintenance/update_references.sh
else
    echo "Actualización de referencias omitida."
fi

echo ""
echo "=== ETAPA 4: Verificación del funcionamiento ==="
echo ""

echo "Ahora debe verificar que el proyecto funcione correctamente con la nueva estructura."
echo "Se recomienda ejecutar las pruebas y verificar que la aplicación se inicie correctamente."
echo ""
echo "Comandos sugeridos para verificar:"
echo "- python -m pytest  # Ejecutar pruebas"
echo "- bash bin/start.sh  # Iniciar la aplicación"
echo ""

read -p "¿Ha verificado que todo funciona correctamente? (s/n): " respuesta
if [[ "$respuesta" != "s" && "$respuesta" != "S" ]]; then
    echo "Por favor, verifique el funcionamiento antes de continuar con la limpieza."
    echo "Puede ejecutar este script nuevamente más tarde para completar el proceso."
    exit 0
fi

echo ""
echo "=== ETAPA 5: Limpieza de archivos duplicados ==="
echo ""

echo "ADVERTENCIA: Esta acción eliminará los archivos originales que han sido copiados a sus nuevas ubicaciones."
echo "Asegúrese de haber verificado que todo funciona correctamente antes de continuar."
echo ""

read -p "¿Desea eliminar los archivos duplicados? (s/n): " respuesta
if [[ "$respuesta" == "s" || "$respuesta" == "S" ]]; then
    bash scripts/maintenance/cleanup_after_reorganization.sh
else
    echo "Limpieza omitida. Puede ejecutar scripts/maintenance/cleanup_after_reorganization.sh más tarde."
fi

echo ""
echo "=================================================================="
echo "      REORGANIZACIÓN COMPLETADA"
echo "=================================================================="
echo ""
echo "La reorganización del proyecto ha sido completada con éxito."
echo "Consulte ESTRUCTURA_PROYECTO.md para obtener información sobre la nueva estructura."
echo ""