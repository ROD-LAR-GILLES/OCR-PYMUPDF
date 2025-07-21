FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    "numpy<2.0.0" \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    transformers==4.35.2 \
    accelerate==0.24.1 \
    torch==2.1.0 \
    -i https://test.pypi.org/simple/ bitsandbytes \
    sentencepiece

# Create app directory
WORKDIR /app

# Copy DeepSeek server code
COPY docker/deepseek/server.py .

# Download model on build (optional, can be mounted)
# RUN python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('deepseek-ai/deepseek-coder-33b-instruct')"

# Expose API port
EXPOSE 8000

# Start server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
