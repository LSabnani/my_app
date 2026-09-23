import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

# Load .env environment variables if present
env_path = BASE_DIR / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# Constants
DEFAULT_LLM_MODEL = os.getenv("GEMINI_MODEL", "gemma-4-26b-a4b-it")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Directory Paths
DATABASE_DIR = BASE_DIR / "database"
SKILLS_DIR = BASE_DIR / "skills"
SAMPLE_DOCS_DIR = BASE_DIR / "sample_docs"
LOG_FILE_PATH = DATABASE_DIR / "log.json"
STATIC_DIR = BASE_DIR / "static"

# Ensure required directories exist
DATABASE_DIR.mkdir(exist_ok=True, parents=True)
SKILLS_DIR.mkdir(exist_ok=True, parents=True)
SAMPLE_DOCS_DIR.mkdir(exist_ok=True, parents=True)
STATIC_DIR.mkdir(exist_ok=True, parents=True)

def get_port():
    """Extract port from command line arguments or environment variable (default: 5000)."""
    parser = argparse.ArgumentParser(description="Agent with RAG Web Application")
    parser.add_argument("--port", type=int, default=None, help="Port to run the Flask application on")
    args, _ = parser.parse_known_args()
    
    if args.port:
        return args.port
    
    env_port = os.getenv("PORT")
    if env_port:
        try:
            return int(env_port)
        except ValueError:
            pass
            
    return 5000
