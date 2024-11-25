# core/security/keys.py
import os
from typing import Dict
from dotenv import load_dotenv
from ..models.config import ModelType

load_dotenv()

API_KEYS: Dict[ModelType, str] = {
    ModelType.CLAUDE: os.getenv("ANTHROPIC_API_KEY", ""),
    ModelType.GPT4O: os.getenv("OPENAI_API_KEY", ""),
    ModelType.O1_PREVIEW: os.getenv("OPENAI_API_KEY", "")
}

def get_api_key(model_type: ModelType) -> str:
    """Get API key for specified model type."""
    key = API_KEYS.get(model_type)
    if not key:
        raise ValueError(f"API key not found for model {model_type}")
    return key