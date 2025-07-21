FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    huggingface_hub \
    transformers

# Configurar el token de Hugging Face si es necesario
# ARG HF_TOKEN
# ENV HUGGINGFACE_TOKEN=$HF_TOKEN

# Descargar el modelo
RUN python -c '\
from huggingface_hub import snapshot_download; \
snapshot_download(\
    "deepseek-ai/deepseek-coder-6.7b-instruct", \
    local_dir="/models", \
    ignore_patterns=["*.md", "*.txt"], \
)'

CMD ["echo", "Model downloaded successfully"]
