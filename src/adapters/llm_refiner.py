"""
Wrapper del modelo OpenAI para limpiar y formatear texto OCR a Markdown.
"""
import os, openai
openai.api_key = os.getenv("OPENAI_API_KEY")

def prompt_refine(raw: str) -> str:
    """
    Alternative LLM-based Markdown formatter using base models like gpt-3.5-turbo or gpt-4o.
    Does not require fine-tuning.
    """
    response = openai.ChatCompletion.create(
        model=os.getenv("OPENAI_PROMPT_MODEL", "gpt-4o"),
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a Markdown formatter for Spanish legal OCR text. "
                    "Convert the user content into well-structured Markdown, preserving "
                    "legal structure, sections, lists, and tables."
                ),
            },
            {"role": "user", "content": raw},
        ],
    )
    return response["choices"][0]["message"]["content"].strip()