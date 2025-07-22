#!/bin/bash

# Script para eliminar archivos duplicados después de la reorganización
# IMPORTANTE: Ejecutar este script solo después de verificar que todo funciona correctamente

echo "Eliminando archivos duplicados después de la reorganización..."

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

echo "Limpieza completada. La nueva estructura de directorios está lista."