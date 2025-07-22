# Estructura del Proyecto OCR-PYMUPDF

Este documento describe la organización del proyecto OCR-PYMUPDF, que sigue una arquitectura hexagonal mientras mantiene una estructura de directorios clara y ordenada.

## Estructura General

```
.
├── .config/               # Configuraciones de herramientas de desarrollo
│   ├── flake8/           # Configuración de linting con Flake8
│   ├── mypy/             # Configuración de verificación de tipos
│   ├── pre-commit/       # Configuración de hooks de pre-commit
│   ├── pytest/           # Configuración de pruebas
│   └── tox/              # Configuración de entornos de prueba
├── bin/                  # Scripts ejecutables y de inicio
├── config/               # Configuraciones globales de la aplicación
├── data/                 # Datos y recursos
│   ├── config/           # Archivos de configuración de datos
│   ├── corrections/      # Datos de correcciones
│   └── dictionaries/     # Diccionarios y patrones
├── docs/                 # Documentación
│   ├── api/              # Documentación de la API
│   ├── developer/        # Documentación para desarrolladores
│   └── user/             # Documentación para usuarios
├── requirements/         # Archivos de dependencias
├── scripts/              # Scripts de utilidad (legacy)
│   ├── data/             # Scripts para gestión de datos
│   ├── deployment/       # Scripts de despliegue
│   └── maintenance/      # Scripts de mantenimiento
├── src/                  # Código fuente (Arquitectura Hexagonal)
│   ├── adapters/         # Adaptadores (implementaciones de puertos)
│   ├── domain/           # Dominio (entidades, casos de uso, puertos)
│   ├── infrastructure/   # Infraestructura (componentes técnicos)
│   └── interfaces/       # Interfaces (CLI, API, etc.)
├── tools/                # Herramientas unificadas
│   ├── bin/              # Ejecutables y scripts Python
│   └── scripts/          # Scripts de shell unificados
└── tests/                # Pruebas
    ├── adapters/         # Pruebas de adaptadores
    ├── domain/           # Pruebas de dominio
    ├── fixtures/         # Archivos de prueba
    ├── infrastructure/   # Pruebas de infraestructura
    └── interfaces/       # Pruebas de interfaces
```

## Arquitectura Hexagonal

El código fuente en `src/` sigue una arquitectura hexagonal (también conocida como puertos y adaptadores):

- **Domain**: El núcleo de la aplicación, contiene la lógica de negocio, entidades, casos de uso y puertos (interfaces).
- **Adapters**: Implementaciones concretas de los puertos definidos en el dominio.
- **Infrastructure**: Componentes técnicos como almacenamiento, caché, logging y HTTP.
- **Interfaces**: Puntos de entrada a la aplicación como CLI, API, etc.

## Archivos de Configuración

Los archivos de configuración se han organizado en directorios específicos:

- `.config/`: Configuraciones de herramientas de desarrollo (linting, pruebas, etc.)
- `config/`: Configuraciones de la aplicación (LLM, OCR, etc.)
- `data/config/`: Configuraciones específicas de datos

## Documentación

La documentación se ha estructurado para diferentes audiencias:

- `docs/api/`: Documentación de la API para integradores
- `docs/developer/`: Documentación para desarrolladores (arquitectura, contribución)
- `docs/user/`: Documentación para usuarios finales

## Scripts y Herramientas

Los scripts se han organizado en dos categorías principales:

### Scripts Legacy (en proceso de migración)

- `scripts/data/`: Scripts para gestión de datos (diccionarios, etc.)
- `scripts/deployment/`: Scripts para despliegue (Docker, etc.)
- `scripts/maintenance/`: Scripts de mantenimiento (actualización de dependencias, limpieza, etc.)

### Herramientas Unificadas

- `tools/scripts/`: Scripts de shell unificados para tareas comunes
  - `api.sh`: Gestión de la API REST (local/Docker)
  - `deps.sh`: Gestión de dependencias
  - `dev.sh`: Gestión del entorno de desarrollo
  - `project.sh`: Gestión del proyecto (reorganización, limpieza)
- `tools/bin/`: Ejecutables y scripts Python
  - `legal_dictionary_manager.py`: Gestor del diccionario de términos legales

## Datos

Los datos se han estructurado de manera más granular:

- `data/config/`: Configuraciones específicas de datos
- `data/corrections/`: Datos de correcciones
- `data/dictionaries/`: Diccionarios y patrones

## Beneficios de esta Organización

1. **Raíz más limpia**: Menos archivos en el directorio raíz
2. **Agrupación lógica**: Archivos relacionados agrupados juntos
3. **Mejor navegabilidad**: Estructura más intuitiva para nuevos desarrolladores
4. **Separación de responsabilidades**: Clara distinción entre código, configuración y recursos
5. **Escalabilidad**: Facilita la adición de nuevos componentes sin desorden