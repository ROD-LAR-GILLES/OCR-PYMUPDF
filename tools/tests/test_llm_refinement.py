from unittest.mock import patch
from adapters.llm_refiner import refine_markdown

def test_refine_markdown_calls_openai():
    fake_md = "### VISTOS\n\nTexto limpio…"
    with patch("openai.ChatCompletion.create") as m:
        m.return_value = {"choices":[{"message":{"content":fake_md}}]}
        out = refine_markdown("VISTOS.- Texto crudo…")
        assert out == fake_md
        m.assert_called_once()