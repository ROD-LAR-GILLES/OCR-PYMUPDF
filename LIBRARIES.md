# Bibliotecas Utilizadas

## Procesamiento de PDFs
### PyMuPDF (fitz) >= 1.23.0
- Biblioteca principal para manejo de PDFs
- Extracción de texto y metadatos
- Renderizado de páginas a imágenes
- Soporte para anotaciones y marcadores
- Alto rendimiento y bajo consumo de memoria

### Camelot-py >= 0.11.0
- Extracción especializada de tablas en PDFs
- Detección automática de estructura tabular
- Soporte para tablas complejas
- Exportación a múltiples formatos

### pdfplumber >= 0.10.3
- Análisis detallado de la estructura PDF
- Extracción precisa de texto con coordenadas
- Identificación de elementos visuales
- Complementa a PyMuPDF en casos específicos

## OCR y Procesamiento de Imágenes
### Tesseract (pytesseract >= 0.3.10)
- Motor OCR principal
- Soporte multilingüe
- Reconocimiento de caracteres y layout
- Integración con OpenCV

### OpenCV (opencv-python >= 4.8.1.78)
- Preprocesamiento de imágenes
- Mejora de calidad para OCR
- Detección de bordes y contornos
- Operaciones de umbralización

### Pillow >= 10.0.0
- Manipulación de imágenes
- Conversión entre formatos
- Optimización de memoria
- Soporte para múltiples formatos

## Procesamiento de Lenguaje Natural
### FastText (fasttext-wheel >= 0.9.2)
- Detección de idiomas
- Clasificación de texto
- Modelo preentrenado con 176 idiomas
- Reemplazo más robusto que langdetect

### langdetect == 1.0.9
- Detección de idiomas (legacy)
- Mantenido para compatibilidad
- Fallback cuando FastText no está disponible

## APIs y Servicios
### OpenAI >= 1.0.0
- Integración con GPT para refinamiento
- Mejora de calidad de texto
- Estructuración de contenido
- Corrección de errores OCR

## Utilidades y Herramientas
### python-dotenv >= 1.0.0
- Gestión de variables de entorno
- Configuración segura
- Separación de credenciales
- Soporte para múltiples entornos

### numpy >= 1.24.3
- Operaciones numéricas
- Procesamiento de matrices
- Soporte para operaciones OCR
- Optimización de rendimiento

### unidecode >= 1.3.8
- Normalización de caracteres
- Manejo de acentos y diacríticos
- Compatibilidad Unicode
- Mejora resultados OCR

## Seguridad y Criptografía
### cryptography >= 42.0.0
- Manejo seguro de credenciales
- Soporte para algoritmos modernos
- Eliminación de advertencias ARC4
- Cumplimiento de estándares

## Testing
### pytest == 7.2.0
- Framework de pruebas unitarias
- Soporte para fixtures
- Marcadores personalizados
- Generación de reportes

## Notas de Versiones
- Las versiones especificadas son mínimas requeridas
- Se recomienda usar las versiones indicadas o superiores
- Algunas dependencias tienen interdependencias específicas
- Se mantiene compatibilidad con Python 3.11+