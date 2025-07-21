"""
Adaptador para refinamiento de texto usando LLMs.
"""
import re
import time
from typing import List, Dict, Any
from domain.ports.llm_port import LLMPort
from domain.ports.llm_provider import LLMProvider
from config.api_settings import load_api_settings
from infrastructure.logging_setup import logger

OCR_PATTERNS = {
    r"[0Oo]": "O",
    r"[1Il]": "l",
    r"[5Ss]": "S",
    r"[8Bb]": "B",
    r"[2Zz]": "Z",
}

def _correct_ocr_errors(text: str) -> str:
    for pattern, replacement in OCR_PATTERNS.items():
        text = re.sub(pattern, replacement, text)
    return text

def _detect_document_structure(text: str) -> Dict[str, List[str]]:
    structure = {"headers": [], "sections": [], "lists": [], "tables": []}
    structure["headers"]  = re.findall(r"^[A-ZÁÉÍÓÚÑ\s]{10,}$", text, re.MULTILINE)
    structure["sections"] = re.findall(r"^\d+\.\s+[A-ZÁÉÍÓÚÑ][^.]+", text, re.MULTILINE)
    structure["lists"]    = re.findall(r"^[\-\*•]\s+.+$",           text, re.MULTILINE)
    return structure


class LLMRefiner(LLMPort):
    """Implementación de LLMPort que refina texto usando diferentes proveedores de LLM."""

    def __init__(self, provider: LLMProvider = None) -> None:
        try:
            self.api_config = load_api_settings()
            
            if provider is None:
                from adapters.providers.openai_provider import OpenAIProvider
                provider = OpenAIProvider()
            
            self.provider = provider
            self.provider.initialize(self.api_config["openai"])
        except Exception as e:
            logger.error(f"Error initializing LLM provider: {e}")
            self.provider = None
            
    def refine_text(self, text: str) -> str:
        """
        Refina y mejora un texto usando LLM.
        
        Args:
            text: Texto a refinar
            
        Returns:
            str: Texto refinado
        """
        if not self.provider:
            logger.warning("LLM provider no disponible, retornando texto sin refinar")
            return text
            
        try:
            refined = self._safe_generate(text, "Refina y mejora este texto manteniendo su estructura.")
            return refined if refined else text
        except Exception as e:
            logger.error(f"Error refinando texto: {e}")
            return text

    def detect_structure(self, text: str) -> dict:
        """
        Detecta la estructura del documento en el texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            dict: Estructura detectada (secciones, listas, etc)
        """
        structure = _detect_document_structure(text)
        
        if self.provider:
            try:
                prompt = "Analiza la estructura de este documento y extrae sus partes principales:"
                llm_structure = self._safe_generate(text, prompt)
                if llm_structure:
                    # TODO: Parsear respuesta del LLM y actualizar structure
                    pass
            except Exception as e:
                logger.error(f"Error detectando estructura con LLM: {e}")
                
        return structure

    def format_markdown(self, text: str) -> str:
        """
        Formatea texto como Markdown usando LLM.
        
        Args:
            text: Texto a formatear
            
        Returns:
            str: Texto formateado en Markdown
        """
        if not self.provider:
            logger.warning("LLM provider no disponible, retornando texto sin formatear")
            return text
            
        try:
            prompt = "Formatea este texto como Markdown, manteniendo su estructura y contenido:"
            formatted = self._safe_generate(text, prompt)
            return formatted if formatted else text
        except Exception as e:
            logger.error(f"Error formateando texto: {e}")
            return text

    def _safe_generate(self, prompt: str, system_prompt: str = None) -> str:
        """
        Safe wrapper for LLM completion generation.
        
        Args:
            prompt: Text to process
            system_prompt: Optional system instructions
            
        Returns:
            Generated completion or original text on error
        """
        try:
            return self.provider.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.1
            )
        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            return prompt

    # ───────────────────── Fine-tuned model ─────────────────────
    def refine_markdown(self, raw_text: str) -> str:
        """Refine OCR text using configured LLM provider."""
        if not self.provider:
            logger.warning("LLM provider not available → returning raw text")
            return raw_text

        system_prompt = ("You are a Markdown formatter for Spanish legal OCR text. "
                        "Convert the user content into well-structured Markdown.")
        
        return self._safe_generate(raw_text, system_prompt) or raw_text

    # ───────────────────── Prompt-based pipeline ─────────────────────
    def prompt_refine(self, raw: str) -> str:
        """Prompt-based refinement pipeline."""
        if not self.provider:
            logger.warning("LLM provider not available → returning raw text")
            return raw

        try:
            cleaned = _correct_ocr_errors(raw)
            structure = _detect_document_structure(cleaned)

            # Initial document analysis
            analysis_prompt = ("You are a legal document analysis expert. "
                           "Analyze the text and return its structure, references, and OCR errors.")
            analysis = self._safe_generate(cleaned, analysis_prompt)

            # Final refinement with context
            system_prompt = (
                "You are an advanced legal document and OCR processing expert.\n"
                f"- Headers detected: {len(structure['headers'])}\n"
                f"- Numbered sections: {len(structure['sections'])}\n"
                f"- List items: {len(structure['lists'])}\n\n"
                f"Previous analysis:\n{analysis}"
            )
            
            return self._safe_generate(cleaned, system_prompt) or raw

        except Exception as e:
            logger.exception(f"Error in refinement pipeline: {e}")
            return raw