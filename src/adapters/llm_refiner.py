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
import os
import re
import openai
from typing import Dict, List

# Configuración OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

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

def prompt_refine(raw: str) -> str:
    """
    Mejora el texto OCR usando GPT con un sistema de prompts especializados.
    
    Args:
        raw: Texto OCR sin procesar
    Returns:
        str: Texto mejorado en formato Markdown
    """
    # 1. Corrección inicial de errores OCR
    cleaned_text = correct_ocr_errors(raw)
    
    # 2. Análisis de estructura
    structure = detect_document_structure(cleaned_text)
    
    # 3. Generar prompt contextual
    system_prompt = (
        "Eres un experto en formateo de documentos legales a Markdown. "
        "Tu tarea es mejorar la estructura y legibilidad del texto manteniendo su contenido legal. "
        "\n\nReglas:\n"
        "1. Usa ### para secciones principales (ej: RESUELVO, CONSIDERANDO)\n"
        "2. Usa #### para subsecciones numeradas\n"
        "3. Preserva las listas numeradas y viñetas\n"
        "4. Mantén el formato de las tablas usando sintaxis Markdown\n"
        "5. Corrige errores obvios de OCR\n"
        "6. Mantén las referencias legales exactas (números de ley, fechas, etc)\n"
        "7. No agregues ni elimines información legal\n"
        "\nEstructura detectada:\n" + 
        f"- Headers: {len(structure['headers'])}\n" +
        f"- Sections: {len(structure['sections'])}\n" +
        f"- Lists: {len(structure['lists'])}"
    )
    
    response = openai.ChatCompletion.create(
        model=os.getenv("OPENAI_PROMPT_MODEL", "gpt-4"),
        temperature=0.1,  # Reducido para mayor precisión
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": cleaned_text}
        ]
    )
    
    return response["choices"][0]["message"]["content"].strip()