# ─── src/adapters/llm_refiner.py ───
import re
from typing import List, Dict, Any
import time
from openai import OpenAI, APIError, RateLimitError
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


class LLMRefiner:
    """Refina texto OCR usando modelos OpenAI."""

    def __init__(self) -> None:
        try:
            self.api_config = load_api_settings()["openai"]
            self.client = OpenAI(
                api_key=self.api_config["api_key"],
                organization=self.api_config["org_id"]
            )
            self.max_retries = 5
        except Exception as e:
            logger.error(f"Error al inicializar cliente OpenAI: {e}")
            self.client = None
            self.api_config = {}
            
    def _safe_chat(self, **kwargs) -> Any:
        """
        Wrapper seguro para llamadas a la API con back-off exponencial.
        
        Args:
            **kwargs: Argumentos para chat.completions.create
            
        Returns:
            La respuesta de la API o levanta una excepción si se agotan los reintentos
        """
        for attempt in range(self.max_retries):
            try:
                return self.client.chat.completions.create(**kwargs)
            except RateLimitError:
                if attempt == self.max_retries - 1:
                    raise
                wait = 2 ** attempt  # Back-off exponencial: 1, 2, 4, 8, 16 segundos
                logger.warning(f"Rate-limit alcanzado, reintentando en {wait}s")
                time.sleep(wait)

    # ───────────────────── Fine-tuned model ─────────────────────
    def refine_markdown(self, raw_text: str) -> str:
        if not self.client:
            logger.warning("Cliente OpenAI no disponible → texto sin refinar")
            return raw_text

        try:
            model_id = self.api_config.get("ft_model") or self.api_config["prompt_model"]
            resp = self._safe_chat(
                model=model_id,
                temperature=0.1,
                messages=[
                    {"role": "system",
                     "content": ("You are a Markdown formatter for Spanish legal OCR text. "
                                 "Convert the user content into well-structured Markdown.")},
                    {"role": "user", "content": raw_text},
                ]
            )
            return resp.choices[0].message.content.strip()
        except RateLimitError:
            logger.warning("Límite de API alcanzado → texto original")
        except APIError as e:
            logger.error(f"API OpenAI: {e}")
        except Exception as e:
            logger.exception(f"Error inesperado: {e}")
        return raw_text

    # ───────────────────── Prompt-based pipeline ─────────────────────
    def prompt_refine(self, raw: str) -> str:
        if not self.client:
            logger.warning("Cliente OpenAI no disponible → texto sin refinar")
            return raw

        try:
            cleaned = _correct_ocr_errors(raw)
            structure = _detect_document_structure(cleaned)

            system_prompt = (
                "Eres un experto en procesamiento avanzado de documentos legales y OCR…\n"
                f"- Encabezados detectados: {len(structure['headers'])}\n"
                f"- Secciones numeradas: {len(structure['sections'])}\n"
                f"- Elementos de lista: {len(structure['lists'])}\n"
            )

            analysis = self._safe_chat(
                model=self.api_config["prompt_model"],
                temperature=0.1,
                messages=[
                    {"role": "system",
                     "content": ("Eres un experto en análisis de documentos legales. Analiza el texto y "
                                 "devuelve su estructura, referencias y errores OCR.")},
                    {"role": "user", "content": cleaned},
                ]
            )

            formatted = self._safe_chat(
                model=self.api_config["prompt_model"],
                temperature=0.1,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "assistant", "content": analysis.choices[0].message.content},
                    {"role": "user", "content": cleaned},
                ],
            )
            return formatted.choices[0].message.content.strip()

        except RateLimitError:
            logger.warning("Límite de API alcanzado → texto original")
        except APIError as e:
            logger.error(f"API OpenAI: {e}")
        except Exception as e:
            logger.exception(f"Error inesperado: {e}")
        return raw