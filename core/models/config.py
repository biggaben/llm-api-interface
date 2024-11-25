# core/models/config.py
from dataclasses import dataclass
from enum import Enum
from typing import List

class ModelType(Enum):
    GPT4O = "gpt-4o"                        # GPT-4o
    O1_PREVIEW = "o1-preview"               # o1-preview
    CLAUDE = "claude-3-5-sonnet-20241022"   # Claude Sonnet (latest)

@dataclass
class ModelConfig:
    model_type: ModelType
    cost_per_1k_input_tokens: float
    cost_per_1k_output_tokens: float
    max_tokens: int
    context_window: int
    capabilities: List[str]
    typical_latency: float  # seconds