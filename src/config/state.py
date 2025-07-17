# src/config/state.py
from dotenv import load_dotenv

"""
Estado global compartido para el modo LLM.

Valores posibles:
    • "off"    → desactiva LLM
    • "ft"     → usa modelo fine-tune
    • "prompt" → usa prompt directo
    • "auto"   → intenta fine-tune y cae a prompt
"""
# Se ejecuta una sola vez al importar `config.state`
load_dotenv()

LLM_MODE = "auto"