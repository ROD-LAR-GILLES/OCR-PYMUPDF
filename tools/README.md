# Herramientas Unificadas para OCR-PYMUPDF

Este directorio contiene herramientas unificadas para la gestión del proyecto OCR-PYMUPDF. Estas herramientas simplifican las tareas comunes y reducen la duplicación de código.

## Estructura

- `scripts/`: Scripts de shell para tareas de gestión del proyecto
- `bin/`: Ejecutables y scripts Python para tareas específicas

## Scripts Disponibles

### Gestión del Proyecto

- `scripts/project.sh`: Script unificado para la gestión del proyecto
  - `project.sh reorganize`: Reorganizar la estructura del proyecto
  - `project.sh cleanup`: Eliminar archivos duplicados después de la reorganización
  - `project.sh update-refs`: Actualizar referencias en el código
  - `project.sh status`: Mostrar el estado actual del proyecto

### Gestión de Dependencias

- `scripts/deps.sh`: Script unificado para la gestión de dependencias
  - `deps.sh update`: Actualizar todas las dependencias
  - `deps.sh base`: Actualizar solo dependencias base
  - `deps.sh dev`: Actualizar solo dependencias de desarrollo
  - `deps.sh api`: Actualizar solo dependencias de la API
  - `deps.sh docs`: Actualizar solo dependencias de documentación
  - `deps.sh check`: Verificar vulnerabilidades de seguridad
  - `deps.sh sync`: Sincronizar el entorno virtual con las dependencias

### Gestión de la API

- `scripts/api.sh`: Script unificado para la ejecución de la API REST
  - `api.sh --local`: Iniciar la API en modo local
  - `api.sh --docker`: Iniciar la API con Docker
  - `api.sh --stop`: Detener la API en Docker

### Gestión del Entorno de Desarrollo

- `scripts/dev.sh`: Script unificado para la gestión del entorno de desarrollo
  - `dev.sh start`: Iniciar el entorno de desarrollo con Docker
  - `dev.sh stop`: Detener el entorno de desarrollo
  - `dev.sh test`: Ejecutar tests
  - `dev.sh docs`: Iniciar servidor de documentación
  - `dev.sh lint`: Ejecutar linters
  - `dev.sh deps`: Actualizar dependencias
  - `dev.sh shell`: Entrar al contenedor

### Herramientas de Datos

- `bin/legal_dictionary_manager.py`: Gestor del diccionario de términos legales
  - `legal_dictionary_manager.py --add TERM`: Añadir un nuevo término al diccionario
  - `legal_dictionary_manager.py --category CAT`: Especificar categoría al añadir un término
  - `legal_dictionary_manager.py --list`: Listar todos los términos
  - `legal_dictionary_manager.py --update`: Actualizar y reorganizar el diccionario

## Uso

Todos los scripts están diseñados para ser ejecutados desde la raíz del proyecto. Por ejemplo:

```bash
# Iniciar la API en modo local
./tools/scripts/api.sh --local

# Actualizar dependencias
./tools/scripts/deps.sh update

# Gestionar el diccionario legal
./tools/bin/legal_dictionary_manager.py --list
```

## Mantenimiento

Estos scripts están diseñados para ser mantenidos en un solo lugar, evitando la duplicación de código y facilitando las actualizaciones. Si necesitas modificar alguna funcionalidad, hazlo directamente en estos scripts unificados en lugar de crear nuevos scripts.