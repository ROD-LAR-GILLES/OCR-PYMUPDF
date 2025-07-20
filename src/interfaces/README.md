# Interfaces Module

## Descripción
Módulo que proporciona interfaces de usuario y puntos de entrada para la aplicación.

## Estructura
```
interfaces/
├── cli_menu.py
└── __init__.py
```

## Componentes

### cli_menu.py
Interfaz de línea de comandos.

#### Clases
- `CLIMenu`
  - `display_menu()`: Muestra opciones
  - `process_input()`: Procesa selección
  - `execute_option()`: Ejecuta opción
  
#### Funciones
- `run_cli()`: Punto de entrada principal
- `process_file(path: str)`: Procesa archivo
- `display_results(result: str)`: Muestra resultados
- `handle_error(error: Exception)`: Maneja errores

## Opciones del Menú
1. Procesar PDF Digital
2. Procesar PDF Escaneado
3. Extraer Tablas
4. Configurar OCR
5. Ver Resultados
6. Salir

## Uso
```python
from interfaces.cli_menu import run_cli

# Ejecutar interfaz CLI
run_cli()

# O usar componentes individuales
menu = CLIMenu()
menu.display_menu()
```

## Características
- Interfaz intuitiva
- Manejo de errores amigable
- Progreso visible
- Ayuda contextual

## Validación de Entrada
- Verificación de rutas
- Validación de opciones
- Confirmación de acciones
- Límites de entrada

## Mensajes de Error
- Errores de archivo
- Errores de procesamiento
- Errores de configuración
- Errores de sistema

## Dependencias
- argparse
- rich (para CLI)
- tabulate

## Notas de Implementación
- Diseño de UI consistente
- Manejo de señales del sistema
- Documentación de comandos
- Tests de integración
