# Herramientas Unificadas - OCR-PYMUPDF

## 🎯 Estructura Completamente Unificada

Todas las herramientas del proyecto están ahora consolidadas en un **único directorio**: `tools/`

```
tools/                              # ÚNICO directorio de herramientas
├── bin/                            # Ejecutables principales
│   ├── run_api.py                  # API principal del proyecto
│   └── run_web.py                  # Interfaz web
├── maintenance/                    # 🔧 Mantenimiento de código
│   ├── clean_emojis.py             # Limpieza de emoticones
│   ├── code_maintenance.sh         # Script integral de mantenimiento
│   └── format_code.sh              # Formateo automático
├── quality/                        # 📊 Análisis de calidad
│   ├── lint_code.sh                # Análisis de código (flake8, mypy, etc.)
│   └── quality_report.sh           # Reportes completos de calidad
├── diagnostics/                    # 🔍 Herramientas de diagnóstico
│   ├── diagnose_api.sh             # Diagnóstico de API
│   ├── diagnose_docker.py          # Diagnóstico de contenedores
│   ├── diagnose_pdf.py             # Diagnóstico de archivos PDF
│   └── diagnose_pdf_docker.sh      # Diagnóstico PDF en Docker
├── security/                       # 🔒 Verificaciones de seguridad
│   └── security_check.sh           # Análisis de vulnerabilidades
├── performance/                    # ⚡ Análisis de rendimiento
│   └── performance_check.sh        # Tests de rendimiento y optimización
├── tests/                          # 🧪 Tests unitarios e integración
│   ├── run_tests.sh                # Tests unitarios principales
│   ├── test_api_routes.sh          # Tests de endpoints API
│   └── test_upload.sh              # Tests de subida de archivos
├── scripts/                        # 📜 Scripts de utilidad
│   ├── legal_dictionary_manager.py # Gestión de diccionarios legales
│   └── data -> ../data             # Enlace a datos compartidos
├── config/                         # ⚙️ Configuraciones
├── data/                           # 📄 Datos del proyecto
├── reports/                        # 📋 Reportes generados
└── tools_master.py                 # 🎛️ Controlador maestro unificado
```

## 🚀 Cómo Usar

### Herramienta Maestra (Recomendado)
```bash
# Ver todas las herramientas disponibles
python3 tools/tools_master.py --list

# Ejecutar herramienta específica
python3 tools/tools_master.py --run maintenance clean_emojis.py --dry-run
python3 tools/tools_master.py --run quality quality_report.sh
python3 tools/tools_master.py --run diagnostics diagnose_pdf.py archivo.pdf

# Suites predefinidas
python3 tools/tools_master.py --maintenance-suite
python3 tools/tools_master.py --quality-suite
```

### Script Principal
```bash
# Opciones específicas
./run_all_tests.sh --clean-emojis      # Solo limpieza de emoticones
./run_all_tests.sh --quality           # Solo análisis de calidad
./run_all_tests.sh --security          # Solo verificación seguridad

# Modos predefinidos
./run_all_tests.sh --quick             # Verificación rápida
./run_all_tests.sh --standard          # Análisis estándar
./run_all_tests.sh --full              # Análisis completo
```

### Acceso Directo
```bash
# Mantenimiento
tools/maintenance/clean_emojis.py --dry-run
tools/maintenance/format_code.sh --apply

# Calidad
tools/quality/lint_code.sh --quick
tools/quality/quality_report.sh

# Diagnóstico
tools/diagnostics/diagnose_pdf.py pdfs/archivo.pdf
tools/diagnostics/diagnose_api.sh

# Tests
tools/tests/run_tests.sh --coverage
```

## 📁 Organización por Función

### 🔧 Mantenimiento (`tools/maintenance/`)
Herramientas para mantener la calidad y limpieza del código:
- **clean_emojis.py**: Elimina emoticones de archivos para compatibilidad
- **code_maintenance.sh**: Script integral de mantenimiento
- **format_code.sh**: Formateo automático con black, isort, etc.

### 📊 Calidad (`tools/quality/`)
Análisis y reportes de calidad de código:
- **lint_code.sh**: Análisis con flake8, mypy, bandit
- **quality_report.sh**: Reportes completos de estado del proyecto

### 🔍 Diagnóstico (`tools/diagnostics/`)
Herramientas para identificar problemas:
- **diagnose_api.sh**: Verifica estado de la API
- **diagnose_docker.py**: Analiza contenedores y configuración
- **diagnose_pdf.py**: Diagnostica problemas con archivos PDF
- **diagnose_pdf_docker.sh**: Diagnóstico PDF en entorno Docker

### 🔒 Seguridad (`tools/security/`)
Verificaciones de seguridad:
- **security_check.sh**: Análisis de vulnerabilidades y dependencias

### ⚡ Rendimiento (`tools/performance/`)
Análisis de rendimiento:
- **performance_check.sh**: Tests de rendimiento y benchmarks

### 🧪 Tests (`tools/tests/`)
Tests del proyecto:
- **run_tests.sh**: Suite principal de tests unitarios
- **test_api_routes.sh**: Tests de endpoints de la API
- **test_upload.sh**: Tests de funcionalidad de subida

## 🎛️ Controlador Maestro

El archivo `tools/tools_master.py` es el **punto de entrada unificado** para todas las herramientas:

```python
# Arquitectura del controlador
class ToolsMaster:
    def run_maintenance_tool(tool, *args)     # tools/maintenance/
    def run_quality_tool(tool, *args)         # tools/quality/
    def run_diagnostic_tool(tool, *args)      # tools/diagnostics/
    def run_security_tool(tool, *args)        # tools/security/
    def run_performance_tool(tool, *args)     # tools/performance/
    def run_unit_test_tool(tool, *args)       # tools/tests/
```

## 📋 Reportes

Todos los reportes se generan en `tools/reports/`:
- **master_report_YYYYMMDD_HHMMSS.txt**: Reporte maestro de sesión
- **quality_report_YYYYMMDD.html**: Reporte de calidad detallado
- **security_scan_YYYYMMDD.json**: Resultados de análisis de seguridad
- **performance_YYYYMMDD.log**: Métricas de rendimiento

## 🔄 Migración Completada

### ✅ Consolidación Exitosa
- ❌ `testing/tools/` (eliminado)
- ❌ `tools/testing/` (eliminado)  
- ❌ Archivos duplicados (eliminados)
- ✅ `tools/` (único directorio unificado)

### ✅ Compatibilidad
- ✅ Script principal (`run_all_tests.sh`) actualizado
- ✅ Todas las rutas corregidas
- ✅ Funcionalidad completa mantenida
- ✅ Nuevas capacidades agregadas

### ✅ Beneficios
- **Simplicidad**: Un solo lugar para todas las herramientas
- **Organización**: Estructura lógica por función
- **Escalabilidad**: Fácil agregar nuevas herramientas
- **Mantenibilidad**: Sin duplicaciones ni confusión

## 🎉 Estado Final

El proyecto ahora tiene una **estructura de herramientas completamente unificada**:

- **1 directorio** en lugar de 3 dispersos
- **6 categorías funcionales** claras
- **0 duplicaciones** de archivos o directorios
- **100% compatibilidad** con código existente
- **Herramienta maestra** para control centralizado

¡La unificación está **completamente terminada** y el sistema es ahora más **simple, organizado y fácil de usar**! 🚀
