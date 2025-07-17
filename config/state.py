# src/config/state.py
"""
Estado global compartido para el modo LLM.

Valores posibles:
    • "off"    → desactiva LLM
    • "ft"     → usa modelo fine-tune
    • "prompt" → usa prompt directo
    • "auto"   → intenta fine-tune y cae a prompt
"""
LLM_MODE = "auto"