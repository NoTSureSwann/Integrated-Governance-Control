import os
from dotenv import load_dotenv

# Load environmental variables from .env file
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

KIMI_API_KEY = os.getenv("KIMI_API_KEY", "").strip()
KIMI_MODEL = os.getenv("KIMI_MODEL", "kimi-k2")
KIMI_BASE_URL = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-large-latest")

MOCK_MODE = os.getenv("MOCK_MODE", "True").lower() in ("true", "1", "yes")

# Database configuration
DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Support for Ollama fallback if user provided an ollama run command
if KIMI_API_KEY.startswith("ollama"):
    parts = KIMI_API_KEY.split()
    if len(parts) > 2 and parts[1] == "run":
        KIMI_MODEL = parts[2]
    KIMI_API_KEY = "ollama"  # Dummy key for OpenAI client
    KIMI_BASE_URL = "http://localhost:11434/v1"

def validate_config():
    """
    Validate that all required API keys are present.
    Returns a list of error messages, or an empty list if valid.
    """
    missing = []
    # Only warn about primary keys needed by default pipeline
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY is missing from environment or .env file.")
    if not KIMI_API_KEY:
        missing.append("KIMI_API_KEY is missing from environment or .env file.")
    return missing
