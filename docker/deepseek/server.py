"""FastAPI server for local DeepSeek model."""
import os
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = FastAPI(title="DeepSeek Local API")

# Load model and tokenizer
MODEL_ID = os.getenv("MODEL_ID", "deepseek-ai/deepseek-coder-1.3b-instruct")  # Smaller model
USE_INT8 = os.getenv("USE_INT8", "false").lower() == "true"  # Enable int8 quantization for memory efficiency
USE_MMAP = os.getenv("USE_MMAP", "true").lower() == "true"  # Enable memory mapping

model = None
tokenizer = None

@app.on_event("startup")
async def load_model():
    """Load model and tokenizer on startup."""
    global model, tokenizer
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=True)
        model_kwargs = {
            "device_map": "auto",  # Let accelerate decide
            "torch_dtype": torch.float32,
            "use_mmap": USE_MMAP  # Use memory mapping if enabled
        }
        
        if USE_INT8:
            model_kwargs.update({
                "torch_dtype": torch.int8,
                "load_in_8bit": True
            })
            
        model = AutoModelForCausalLM.from_pretrained(MODEL_ID, **model_kwargs)
    except Exception as e:
        print(f"Error loading model: {e}")
        raise

@app.post("/v1/chat/completions")
async def chat_completion(request: Dict[str, Any]) -> Dict[str, Any]:
    """Generate chat completion using DeepSeek model.
    
    Args:
        request: Dictionary containing:
            - messages: List of message dictionaries
            - temperature: Optional float for randomness
            - max_tokens: Optional int for response length
            
    Returns:
        Dictionary containing model response
    """
    try:
        messages: List[Dict[str, str]] = request["messages"]
        temperature: float = request.get("temperature", 0.1)
        max_tokens: int = request.get("max_tokens", 1000)
        
        # Format messages into prompt
        prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt += f"System: {content}\n"
            elif role == "user":
                prompt += f"User: {content}\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n"
        prompt += "Assistant: "
        
        # Generate response
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=temperature > 0,
            pad_token_id=tokenizer.eos_token_id
        )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract assistant's response
        response = response.split("Assistant: ")[-1].strip()
        
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": response
                },
                "finish_reason": "stop"
            }]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
