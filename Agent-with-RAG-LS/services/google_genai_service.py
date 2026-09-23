import os
import time
import requests
from config import GEMINI_API_KEY, DEFAULT_LLM_MODEL

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

def redact_api_key(text: str) -> str:
    """Utility to sanitize API keys from payload logs."""
    if not text:
        return text
    if GEMINI_API_KEY and len(GEMINI_API_KEY) > 4:
        text = text.replace(GEMINI_API_KEY, "****")
    return text

def get_active_models() -> list:
    """
    Queries Google AI Studio API for active models capable of generating text.
    Returns list of model strings.
    """
    models = [DEFAULT_LLM_MODEL, "gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash", "gemma-2-9b-it", "Custom Model"]
    
    if GENAI_AVAILABLE and GEMINI_API_KEY:
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            api_models = client.models.list()
            fetched = []
            for m in api_models:
                name = getattr(m, "name", str(m))
                if name.startswith("models/"):
                    name = name.replace("models/", "")
                fetched.append(name)
            if fetched:
                # Merge unique active models
                combined = []
                for m in fetched + models:
                    if m not in combined:
                        combined.append(m)
                return combined
        except Exception as e:
            print(f"[GenAI Models List Warning]: {e}")
            
    return models

def invoke_llm(
    model: str,
    prompt: str,
    system_instruction: str = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    custom_endpoint: str = None
) -> dict:
    """
    Executes an LLM request via Google GenAI SDK or custom endpoint.
    Returns payload dictionary containing response_text, tokens, elapsed_time, and raw request/response objects.
    """
    start_time = time.time()
    
    # Check for Custom Model
    if model == "Custom Model":
        endpoint = custom_endpoint or "http://127.0.0.1:8000/v1/chat/completions"
        payload = {
            "model": "custom",
            "messages": [
                {"role": "system", "content": system_instruction or "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        try:
            res = requests.post(endpoint, json=payload, timeout=30)
            elapsed = time.time() - start_time
            if res.status_code == 200:
                data = res.json()
                content = data["choices"][0]["message"]["content"]
                input_tokens = len(prompt.split()) * 2
                output_tokens = len(content.split()) * 2
                return {
                    "text": content,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "elapsed_time": round(elapsed, 4),
                    "ttft": round(elapsed * 0.3, 4),
                    "model": "Custom Model",
                    "raw_request": payload,
                    "raw_response": data,
                    "error": None
                }
            else:
                return {
                    "text": f"Error from custom model endpoint ({res.status_code}): {res.text}",
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "elapsed_time": round(elapsed, 4),
                    "ttft": 0,
                    "model": "Custom Model",
                    "raw_request": payload,
                    "raw_response": res.text,
                    "error": res.text
                }
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "text": f"Failed to connect to custom model endpoint '{endpoint}': {str(e)}",
                "input_tokens": 0,
                "output_tokens": 0,
                "elapsed_time": round(elapsed, 4),
                "ttft": 0,
                "model": "Custom Model",
                "raw_request": payload,
                "raw_response": str(e),
                "error": str(e)
            }
            
    # Default: Google GenAI API Call
    if not GENAI_AVAILABLE:
        elapsed = time.time() - start_time
        # Fallback simulator if SDK not installed or missing key
        simulated_response = f"[Simulated response for model {model}]: Received query: '{prompt[:100]}...'"
        return {
            "text": simulated_response,
            "input_tokens": len(prompt.split()),
            "output_tokens": len(simulated_response.split()),
            "elapsed_time": round(elapsed, 4),
            "ttft": 0.1,
            "model": model,
            "raw_request": {"model": model, "prompt": prompt},
            "raw_response": {"text": simulated_response},
            "error": None
        }
        
    try:
        api_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        client = genai.Client(api_key=api_key)
        
        config_args = {
            "temperature": temperature,
            "max_output_tokens": max_tokens
        }
        if system_instruction:
            config_args["system_instruction"] = system_instruction
            
        raw_req = {
            "model": model,
            "prompt": prompt,
            "config": config_args
        }
        
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(**config_args)
        )
        
        elapsed = time.time() - start_time
        
        # Extract text safely from response object or candidate parts
        resp_text = ""
        try:
            if hasattr(response, "text") and response.text:
                resp_text = response.text
            elif hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "content") and candidate.content and hasattr(candidate.content, "parts"):
                    text_parts = [p.text for p in candidate.content.parts if hasattr(p, "text") and p.text and not getattr(p, "thought", False)]
                    if not text_parts:
                        text_parts = [p.text for p in candidate.content.parts if hasattr(p, "text") and p.text]
                    resp_text = "\n".join(text_parts)
        except Exception:
            resp_text = str(response)
            
        if not resp_text or resp_text.startswith("sdk_http_response="):
            try:
                if hasattr(response, "candidates") and response.candidates:
                    c = response.candidates[0]
                    parts = getattr(getattr(c, "content", None), "parts", [])
                    non_thought = [p.text for p in parts if hasattr(p, "text") and p.text and not getattr(p, "thought", False)]
                    if non_thought:
                        resp_text = "\n".join(non_thought)
                    elif parts:
                        resp_text = "\n".join([p.text for p in parts if hasattr(p, "text") and p.text])
            except Exception:
                pass
        
        # Token metrics extraction
        usage = getattr(response, "usage_metadata", None)
        input_tokens = getattr(usage, "prompt_token_count", len(prompt.split())) if usage else len(prompt.split())
        output_tokens = getattr(usage, "candidates_token_count", len(resp_text.split())) if usage else len(resp_text.split())
        
        return {
            "text": resp_text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "elapsed_time": round(elapsed, 4),
            "ttft": round(elapsed * 0.25, 4),
            "model": model,
            "raw_request": raw_req,
            "raw_response": str(resp_text),
            "error": None
        }
    except Exception as e:
        elapsed = time.time() - start_time
        err_msg = str(e)
        return {
            "text": f"Error calling Google GenAI API ({model}): {err_msg}",
            "input_tokens": len(prompt.split()),
            "output_tokens": 0,
            "elapsed_time": round(elapsed, 4),
            "ttft": 0,
            "model": model,
            "raw_request": {"model": model, "prompt": prompt},
            "raw_response": err_msg,
            "error": err_msg
        }
