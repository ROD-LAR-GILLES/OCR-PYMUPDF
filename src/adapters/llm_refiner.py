"""
Wrapper del modelo fine-tuneado (o base) de OpenAI para limpiar Markdown.
"""
import os, openai
openai.api_key = os.getenv("OPENAI_API_KEY")

MODEL_ID = os.getenv("OPENAI_FT_MODEL", "gpt-3.5-turbo")

_SYSTEM = (
    "You are a Markdown formatter for Spanish legal OCR text. "
    "Convert the user content into well-structured Markdown."
)

def refine_markdown(raw_text: str) -> str:
    rsp = openai.ChatCompletion.create(
        model=MODEL_ID,
        temperature=0.2,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user",   "content": raw_text}
        ],
    )
    return rsp["choices"][0]["message"]["content"].strip()

def prompt_refine(raw: str) -> str:
    """
    Alternative LLM-based Markdown formatter using base models like gpt-3.5-turbo or gpt-4o.
    Does not require fine-tuning.
    """
    response = openai.ChatCompletion.create(
        model=os.getenv("OPENAI_PROMPT_MODEL", "gpt-4o"),  # puedes cambiar a gpt-3.5-turbo si prefieres
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