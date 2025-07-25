#   Testing Suite - OCR-PYMUPDF

Este directorio contiene todas las herramientas de testing, análisis de calidad, seguridad y rendimiento para el proyecto OCR-PYMUPDF.

##   Inicio Rápido

Para ejecutar todas las verificaciones de una vez:

```bash
# Desde la raíz del proyecto
./run_all_tests.sh --standard
```

##   Estructura del Directorio

```
testing/
├── tools/           # Herramientas de análisis
├── reports/         # Reportes generados
└── README.md       # Esta documentación
```

##   Herramientas Disponibles

###   Script Maestro
- **`../run_all_tests.sh`** - Ejecuta todas las herramientas de testing

###   Herramientas Individuales
- **`tools/lint_code.sh`** - Análisis de calidad de código (como VS Code)
- **`tools/format_code.sh`** - Formateo automático de código
- **`tools/quality_report.sh`** - Reporte completo de calidad
- **`tools/run_tests.sh`** - Ejecución de tests unitarios
- **`tools/security_check.sh`** - Análisis de seguridad
- **`tools/performance_check.sh`** - Análisis de rendimiento

##   Modos de Uso

###   Modo Rápido (5-10 minutos)
```bash
./run_all_tests.sh --quick
```
- Tests unitarios básicos
- Análisis rápido de código
- Verificación de sintaxis

###   Modo Estándar (15-20 minutos)
```bash
./run_all_tests.sh --standard
```
- Tests completos
- Análisis de calidad
- Verificación de seguridad

###   Modo Completo (30+ minutos)
```bash
./run_all_tests.sh --full
```
- Todo lo anterior
- Análisis de rendimiento
- Cobertura de código
- Análisis detallado de seguridad

### 🤖 Modo CI/CD
```bash
./run_all_tests.sh --ci
```
- Solo errores críticos
- Sin output verbose
- Optimizado para pipelines

##   Herramientas Específicas

###   Análisis de Código
```bash
# Análisis rápido (como VS Code Problems)
./testing/tools/lint_code.sh --quick

# Análisis completo
./testing/tools/lint_code.sh
```

###   Formateo de Código
```bash
# Ver cambios sin aplicar
./testing/tools/format_code.sh --dry-run

# Aplicar formateo automático
./testing/tools/format_code.sh --apply
```

###   Tests Unitarios
```bash
# Tests básicos
./testing/tools/run_tests.sh

# Tests con cobertura
./testing/tools/run_tests.sh --coverage

# Tests de rendimiento
./testing/tools/run_tests.sh --performance
```

###   Seguridad
```bash
# Análisis básico
./testing/tools/security_check.sh

# Análisis detallado
./testing/tools/security_check.sh --detailed
```

###   Rendimiento
```bash
# Verificación básica
./testing/tools/performance_check.sh

# Benchmark completo
./testing/tools/performance_check.sh --full

# Monitoreo en tiempo real
./testing/tools/performance_check.sh --monitor
```

##   Reportes

Todos los reportes se generan en `testing/reports/` con timestamp único:

- `master_report_YYYYMMDD_HHMMSS.txt` - Resumen ejecutivo completo
- `quality_report_YYYYMMDD_HHMMSS.txt` - Análisis de calidad de código
- `test_report_YYYYMMDD_HHMMSS.txt` - Resultados de tests
- `security_report_YYYYMMDD_HHMMSS.txt` - Análisis de seguridad
- `performance_report_YYYYMMDD_HHMMSS.txt` - Análisis de rendimiento
- `coverage_html/` - Reporte de cobertura HTML

##   Casos de Uso Comunes

### Desarrollo Diario
```bash
./run_all_tests.sh --quick --verbose
```

### Antes de Commit
```bash
./run_all_tests.sh --standard
```

### Release Preparation
```bash
./run_all_tests.sh --full --coverage
```

### CI/CD Pipeline
```bash
./run_all_tests.sh --ci
```

### Solo Formatear Código
```bash
./run_all_tests.sh --format
```

### Solo Verificar Seguridad
```bash
./run_all_tests.sh --security --verbose
```

##   Estados y Códigos de Salida

- **0** - Todas las verificaciones pasaron
- **1** - Error en prerrequisitos o configuración
- **2** - Tests fallaron
- **3** - Problemas de calidad críticos
- **4** - Vulnerabilidades de seguridad encontradas

##   Prerrequisitos

- Docker y docker-compose instalados
- Contenedor `ocr-pymupdf-api` disponible
- Ejecutar desde la raíz del proyecto OCR-PYMUPDF

##   Personalización

Puedes modificar los scripts en `tools/` para:
- Ajustar umbrales de calidad
- Agregar nuevas verificaciones
- Cambiar formatos de reporte
- Integrar nuevas herramientas

##   Tips y Trucos

1. **Desarrollo iterativo**: Usa `--quick` durante desarrollo
2. **Formateo automático**: Ejecuta `--format` antes de commits
3. **Análisis profundo**: Usa `--full` antes de releases
4. **CI/CD**: Usa `--ci` en pipelines automatizados
5. **Verbose**: Agrega `--verbose` para debug detallado

## 🆘 Troubleshooting

### Contenedor no responde
```bash
docker-compose down && docker-compose up -d
```

### Permisos de scripts
```bash
chmod +x testing/tools/*.sh run_all_tests.sh
```

### Limpiar reportes antiguos
```bash
find testing/reports/ -name "*.txt" -mtime +7 -delete
```

##   Referencias

- **Flake8**: Análisis de código Python
- **MyPy**: Verificación de tipos
- **Black**: Formateo de código
- **Bandit**: Análisis de seguridad
- **Safety**: Verificación de dependencias vulnerables
- **Pytest**: Framework de testing

---

**¡Happy Testing!  **

Para soporte adicional, consulta la documentación individual de cada herramienta usando `--help`.
