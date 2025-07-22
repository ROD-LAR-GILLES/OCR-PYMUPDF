#!/bin/bash

# Script para actualizar referencias a archivos que han sido movidos
# Este script debe ejecutarse después de la reorganización

echo "Actualizando referencias a archivos movidos..."

# Función para buscar y reemplazar en todos los archivos
buscar_reemplazar() {
    local buscar=$1
    local reemplazar=$2
    local extension=$3
    
    echo "Buscando '$buscar' y reemplazando con '$reemplazar' en archivos $extension"
    
    # Excluir directorios .git, .trae, venv, etc.
    find . -type f -name "*.$extension" \
        -not -path "*/.git/*" \
        -not -path "*/.trae/*" \
        -not -path "*/venv/*" \
        -not -path "*/.venv/*" \
        -not -path "*/bin/*" \
        -exec grep -l "$buscar" {} \; | \
    xargs -I{} sed -i '' "s|$buscar|$reemplazar|g" {}
}

# Actualizar referencias a archivos de configuración
buscar_reemplazar ".flake8" ".config/flake8/.flake8" "py"
buscar_reemplazar "mypy.ini" ".config/mypy/mypy.ini" "py"
buscar_reemplazar "pytest.ini" ".config/pytest/pytest.ini" "py"
buscar_reemplazar "tox.ini" ".config/tox/tox.ini" "py"
buscar_reemplazar ".pre-commit-config.yaml" ".config/pre-commit/.pre-commit-config.yaml" "py"

# Actualizar referencias a scripts
buscar_reemplazar "scripts/legal_dictionary_manager.py" "scripts/data/legal_dictionary_manager.py" "py"
buscar_reemplazar "scripts/update_dependencies.sh" "scripts/maintenance/update_dependencies.sh" "py"
buscar_reemplazar "run_api_docker.sh" "scripts/deployment/run_api_docker.sh" "py"

# Actualizar referencias a datos
buscar_reemplazar "data/legal_words.txt" "data/dictionaries/legal_words.txt" "py"
buscar_reemplazar "data/legal_patterns.txt" "data/dictionaries/legal_patterns.txt" "py"
buscar_reemplazar "data/corrections.csv" "data/corrections/corrections.csv" "py"
buscar_reemplazar "data/ocr.json" "data/config/ocr.json" "py"

# Actualizar referencias a archivos de ejecución
buscar_reemplazar "run_api.py" "bin/run_api.py" "py"
buscar_reemplazar "run_api_local.sh" "bin/run_api_local.sh" "py"
buscar_reemplazar "start.sh" "bin/start.sh" "py"

# Actualizar referencias a requisitos
buscar_reemplazar "requirements/requirements.txt" "requirements/base.txt" "py"
buscar_reemplazar "requirements/api-requirements.txt" "requirements/api.txt" "py"
buscar_reemplazar "requirements/requirements-dev.txt" "requirements/dev.txt" "py"

# También buscar en archivos sh
buscar_reemplazar ".flake8" ".config/flake8/.flake8" "sh"
buscar_reemplazar "mypy.ini" ".config/mypy/mypy.ini" "sh"
buscar_reemplazar "pytest.ini" ".config/pytest/pytest.ini" "sh"
buscar_reemplazar "tox.ini" ".config/tox/tox.ini" "sh"

# Buscar en archivos yaml/yml
buscar_reemplazar ".flake8" ".config/flake8/.flake8" "yml"
buscar_reemplazar ".flake8" ".config/flake8/.flake8" "yaml"
buscar_reemplazar "mypy.ini" ".config/mypy/mypy.ini" "yml"
buscar_reemplazar "mypy.ini" ".config/mypy/mypy.ini" "yaml"

echo "Actualización de referencias completada."