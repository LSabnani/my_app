import os
import time
import requests
import subprocess
import numpy as np

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
CURRENT_EMBED_MODEL = "nomic-embed-text"
OLLAMA_PROCESS = None
SPAWNED_BY_APP = False

AVAILABLE_EMBEDDING_MODELS = [
    {
        "name": "nomic-embed-text",
        "dimensions": 768,
        "context_window": "8192 tokens",
        "size": "274 MB",
        "description": "High-performance open text embedding model optimized for short and long context retrieval.",
        "status": "Active"
    },
    {
        "name": "all-minilm",
        "dimensions": 384,
        "context_window": "512 tokens",
        "size": "120 MB",
        "description": "Lightweight and fast sentence transformer embedding model ideal for rapid search.",
        "status": "Available to Pull"
    },
    {
        "name": "mxbai-embed-large",
        "dimensions": 1024,
        "context_window": "512 tokens",
        "size": "670 MB",
        "description": "State-of-the-art sentence embedding model for enterprise search density.",
        "status": "Available to Pull"
    },
    {
        "name": "bge-m3",
        "dimensions": 1024,
        "context_window": "8192 tokens",
        "size": "1.2 GB",
        "description": "Multi-lingual, multi-functionality embedding model supporting long context.",
        "status": "Available to Pull"
    }
]

def check_ollama_running() -> bool:
    """Checks if Ollama server is responding at host URL."""
    try:
        res = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
        return res.status_code == 200
    except Exception:
        return False

def ensure_ollama_started():
    """Starts Ollama background process if not already running."""
    global OLLAMA_PROCESS, SPAWNED_BY_APP
    if check_ollama_running():
        SPAWNED_BY_APP = False
        return True
    
    try:
        # Attempt to launch Ollama background process
        OLLAMA_PROCESS = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        SPAWNED_BY_APP = True
        # Wait up to 3 seconds for server to start
        for _ in range(6):
            time.sleep(0.5)
            if check_ollama_running():
                return True
    except Exception as e:
        print(f"[Ollama Service Warning] Could not spawn 'ollama serve': {e}")
        
    return check_ollama_running()

def shutdown_ollama_if_started_by_app():
    """Terminates Ollama process only if it was spawned by this app."""
    global OLLAMA_PROCESS, SPAWNED_BY_APP
    if SPAWNED_BY_APP and OLLAMA_PROCESS:
        try:
            OLLAMA_PROCESS.terminate()
            OLLAMA_PROCESS.wait(timeout=3)
        except Exception:
            OLLAMA_PROCESS.kill()
        OLLAMA_PROCESS = None
        SPAWNED_BY_APP = False

def get_current_embed_model() -> str:
    return CURRENT_EMBED_MODEL

def set_current_embed_model(model_name: str) -> bool:
    global CURRENT_EMBED_MODEL
    CURRENT_EMBED_MODEL = model_name
    for m in AVAILABLE_EMBEDDING_MODELS:
        if m["name"] == model_name:
            m["status"] = "Active"
        elif m["status"] == "Active":
            m["status"] = "Installed"
    return True

def get_embedding(text: str) -> list:
    """
    Generates embedding vector for input text via Ollama API.
    Falls back to deterministic hash-vector generator if Ollama is unreachable.
    """
    if check_ollama_running():
        try:
            payload = {"model": CURRENT_EMBED_MODEL, "prompt": text}
            res = requests.post(f"{OLLAMA_HOST}/api/embeddings", json=payload, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if "embedding" in data:
                    return data["embedding"]
        except Exception as e:
            print(f"[Ollama Embedding API Error]: {e}")
            
    # Deterministic fallback embedding for testing/standalone operations (768 dimensions)
    np.random.seed(abs(hash(text)) % (2**32))
    vec = np.random.randn(768)
    norm = np.linalg.norm(vec)
    return (vec / norm if norm != 0 else vec).tolist()
