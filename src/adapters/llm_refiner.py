"""
Wrapper del modelo OpenAI para limpiar y formatear texto OCR a Markdown.
Especializado en documentos legales y administrativos.

Características:
- Detecta y corrige errores comunes de OCR
- Estructura secciones y subsecciones
- Formatea listas y enumeraciones
- Preserva tablas y elementos especiales
- Mejora la legibilidad del documento
"""
import re
from typing import List, Dict, Any
from openai import OpenAI
from openai.types.error import APIError, RateLimitError

from src.config.api_settings import api_config, load_api_settings
from src.infrastructure.logging_setup import logger

# Inicializar el cliente de OpenAI con la configuración validada
class LLMRefiner:
    def __init__(self):
        try:
            self.api_config = load_api_settings()["openai"]
            self.client = OpenAI(
                api_key=self.api_config["api_key"],
                organization=self.api_config["org_id"]
            )
        except Exception as e:
            logger.error(f"Error al inicializar cliente OpenAI: {e}")
            self.client = None
            self.api_config = None

# Patrones comunes de errores OCR
OCR_PATTERNS = {
    r'[0Oo]': 'O',  # Confusión 0/O
    r'[1Il]': 'l',  # Confusión 1/I/l
    r'[5Ss]': 'S',  # Confusión 5/S
    r'[8Bb]': 'B',  # Confusión 8/B
    r'[2Zz]': 'Z',  # Confusión 2/Z
}

def correct_ocr_errors(text: str) -> str:
    """Corrige errores comunes de OCR basados en patrones conocidos."""
    for pattern, replacement in OCR_PATTERNS.items():
        text = re.sub(pattern, replacement, text)
    return text

def detect_document_structure(text: str) -> Dict[str, List[str]]:
    """Detecta la estructura básica del documento."""
    structure = {
        "headers": [],
        "sections": [],
        "lists": [],
        "tables": []
    }
    
    # Detectar encabezados
    headers = re.findall(r'^[A-ZÁÉÍÓÚÑ\s]{10,}$', text, re.MULTILINE)
    structure["headers"] = headers
    
    # Detectar secciones numeradas
    sections = re.findall(r'^\d+\.\s+[A-ZÁÉÍÓÚÑ][^.]+', text, re.MULTILINE)
    structure["sections"] = sections
    
    # Detectar listas
    lists = re.findall(r'^[\-\*•]\s+.+$', text, re.MULTILINE)
    structure["lists"] = lists
    
    return structure

def refine_markdown(self, raw_text: str) -> str:
    """
    Mejora el texto usando el modelo fine-tuneado de OpenAI.
    
    Args:
        raw_text: Texto OCR sin procesar
    Returns:
        str: Texto mejorado en formato Markdown o texto original si hay error
    """
    if not self.client:
        logger.warning("Cliente OpenAI no disponible - retornando texto sin procesar")
        return raw_text
        
    try:
        model_id = self.api_config["ft_model"] or self.api_config["prompt_model"]
        
        response = self.client.chat.completions.create(
            model=model_id,
            temperature=0.1,
            messages=[
                {"role": "system", "content": "You are a Markdown formatter for Spanish legal OCR text. Convert the user content into well-structured Markdown."},
                {"role": "user", "content": raw_text}
            ]
        )
        return response.choices[0].message.content.strip()
    except RateLimitError:
        logger.warning("Límite de API alcanzado - retornando texto sin procesar")
        return raw_text
    except APIError as e:
        logger.error(f"Error de API OpenAI: {e}")
        return raw_text
    except Exception as e:
        logger.exception(f"Error inesperado al refinar texto: {e}")
        return raw_text

def prompt_refine(self, raw: str) -> str:
    """
    Mejora el texto OCR usando GPT con un sistema de prompts especializados.
    
    Args:
        raw: Texto OCR sin procesar
    Returns:
        str: Texto mejorado en formato Markdown o texto original si hay error
    """
    if not self.client:
        logger.warning("Cliente OpenAI no disponible - retornando texto sin procesar")
        return raw
        
    try:
        # 1. Corrección inicial de errores OCR
        cleaned_text = correct_ocr_errors(raw)
        
        # 2. Análisis de estructura
        structure = detect_document_structure(cleaned_text)
        
        # 3. Generar prompt contextual mejorado
        system_prompt = (
            "Eres un experto en procesamiento avanzado de documentos legales y OCR, "
            "especializado en mejorar la calidad y estructura del texto manteniendo la "
            "precisión legal. Utilizando las capacidades del modelo gpt-4.1, tu objetivo "
            "es realizar un análisis profundo del texto para:\n\n"
            "1. Comprender el contexto semántico completo del documento\n"
            "2. Identificar y corregir errores de OCR manteniendo la precisión legal\n"
            "3. Estructurar el contenido de forma jerárquica y coherente\n\n"
            
            "OBJETIVOS PRINCIPALES:\n"
            "1. Mejorar la coherencia semántica del texto\n"
            "2. Eliminar ruido y caracteres sin sentido del OCR\n"
            "3. Estructurar y formatear el contenido profesionalmente\n"
            "4. Preservar toda la información legal relevante\n\n"
            
            "REGLAS DE FORMATEO:\n"
            "1. TÍTULOS Y JERARQUÍA:\n"
            "   - # para el título principal del documento\n"
            "   - ## para divisiones principales\n"
            "   - ### para secciones importantes (VISTOS, CONSIDERANDO, RESUELVO)\n"
            "   - #### para subsecciones numeradas\n"
            "   - ##### para subdivisiones menores\n\n"
            
            "2. CONTENIDO Y ESTRUCTURA:\n"
            "   - Identifica y corrige errores típicos de OCR (ej: 'l' por '1', 'O' por '0')\n"
            "   - Mantén la numeración exacta de artículos y referencias legales\n"
            "   - Preserva fechas, números de ley y cifras precisas\n"
            "   - Estructura párrafos lógicamente con líneas en blanco\n\n"
            
            "3. LISTAS Y ENUMERACIONES:\n"
            "   - Usa '1.' para listas numeradas legales\n"
            "   - Usa '-' para viñetas simples\n"
            "   - Mantén la indentación correcta en listas anidadas\n\n"
            
            "4. TABLAS:\n"
            "   - Usa sintaxis Markdown estándar para tablas\n"
            "   - Alinea columnas apropiadamente (izquierda para texto, derecha para números)\n"
            "   - Incluye encabezados descriptivos\n"
            "   - Simplifica tablas complejas manteniendo la información esencial\n\n"
            
            "CONTEXTO DEL DOCUMENTO ACTUAL:\n" + 
            f"- Encabezados detectados: {len(structure['headers'])}\n" +
            f"- Secciones numeradas: {len(structure['sections'])}\n" +
            f"- Elementos de lista: {len(structure['lists'])}\n\n"
            
            "INSTRUCCIONES FINALES:\n"
            "1. Analiza el contexto completo antes de procesar\n"
            "2. Mantén el significado legal exacto\n"
            "3. Mejora la legibilidad sin alterar el contenido\n"
            "4. Conserva la estructura jerárquica original\n"
            "5. Elimina caracteres y secuencias sin sentido semántico\n"
        )
        
        # 4. Realizar refinamiento en dos pasos
        
        # Paso 1: Análisis y limpieza semántica
        analysis_response = self.client.chat.completions.create(
            model=self.api_config["prompt_model"],
            temperature=0.1,
            messages=[
                {"role": "system", "content": 
                    "Eres un experto en análisis de documentos legales. "
                    "Analiza el texto y identifica:\n"
                    "1. Estructura principal del documento\n"
                    "2. Secciones y subsecciones\n"
                    "3. Referencias legales importantes\n"
                    "4. Errores evidentes de OCR\n"
                    "Proporciona esta información de manera estructurada."
                },
                {"role": "user", "content": cleaned_text}
            ]
        )
        
        # Paso 2: Formateo final con contexto del análisis
        format_response = self.client.chat.completions.create(
            model=self.api_config["prompt_model"],
            temperature=0.1,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "assistant", "content": analysis_response.choices[0].message.content},
                {"role": "user", "content": cleaned_text}
            ]
        )
        
        return format_response.choices[0].message.content.strip()
    except RateLimitError:
        logger.warning("Límite de API alcanzado - retornando texto original")
        return raw
    except APIError as e:
        logger.error(f"Error de API OpenAI: {e}")
        return raw
    except Exception as e:
        logger.exception(f"Error inesperado al refinar texto: {e}")
        return raw