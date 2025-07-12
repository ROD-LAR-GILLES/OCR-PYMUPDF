# Instrucciones para Copilot - OCR-RAG

## REGLAS FUNDAMENTALES (CRÍTICAS)

### REGLA #1: SIN EMOTICONES
- **NUNCA** usar emoticones en código, commits o documentación
- **NUNCA** usar símbolos Unicode decorativos (check, cross, rocket, chart, bulb, wrench etc.)
- Solo texto ASCII estándar (+, -, *, [OK], [ERROR])
- Reemplazar emoticones existentes por texto descriptivo

### REGLA #2: CONVENTIONAL COMMITS
- **SIEMPRE** formato: `tipo(scope): descripción`
- Tipos válidos: feat, fix, docs, style, refactor, test, chore
- Ejemplo: `feat: add PDF chunking functionality`
- Incluir cuerpo descriptivo cuando sea necesario

### REGLA #3: ESTILO PROFESIONAL
- Código limpio y legible
- Documentación sin decoraciones visuales
- Mensajes claros y directos
- Mantener consistencia en todo el proyecto

## Estilo de Código

### Nomenclatura
- Usar `snake_case` para nombres de variables y funciones
- Usar `PascalCase` para clases
- Nombres descriptivos y en español cuando sea apropiado

### Documentación
- Todas las funciones deben incluir docstrings estilo Google
- Comentarios en español
- Sin emoticones en docstrings o comentarios

### Imports y Formato
- Evitar `from module import *` — usar imports explícitos
- Usar `f-strings` en lugar de concatenaciones con `+`
- Añadir type hints en todas las funciones
- Seguir PEP 8

## Arquitectura

### Principios
- Aplicar principios de Clean Architecture
- Separar lógica de negocio (dominio) de lógica técnica (adaptadores)
- Seguir patrones como Command y Dependency Injection
- Cada archivo debe tener una sola responsabilidad

## Buenas Prácticas

### Desarrollo
- Evitar código duplicado
- Modularizar: una responsabilidad por archivo
- Tests para funcionalidades críticas
- Logging sin emoticones

### Git y Commits
- Commits atómicos y descriptivos
- Utilizar la Convention de Commit
- Commit deben ser en idioma ingles
- Revisar reglas antes de cada commit
- Verificar ausencia de emoticones antes de commit

## Verificaciones Obligatorias

Antes de cada cambio verificar:
- [ ] Sin emoticones en archivos modificados
- [ ] Mensaje de commit sigue convención
- [ ] Código mantiene estilo consistente
- [ ] Documentación actualizada si es necesario
- [ ] Type hints incluidos en funciones nuevas

## Comandos Útiles

```bash
# Buscar emoticones en el proyecto
grep -r "[\u{1F600}-\u{1F64F}]" . || echo "Sin emoticones encontrados"

# Verificar formato de commits
git log --oneline -5

# Revisar archivos modificados
git status

# Ignorar este archivo del repositorio
echo "README.copilot.md" >> .git/info/exclude
```

## Configuración Docker (Referencia)

```bash
# Construir y ejecutar
docker compose up --build -d

# Ejecutar CLI en contenedor
docker exec -it ocr-cli-ocr-backend-1 python interfaces/cli/main.py
```

---

## RECORDATORIO CRÍTICO
**REVISAR ESTAS REGLAS ANTES DE CADA CAMBIO**
**PRIORIDAD #1: SIN EMOTICONES**