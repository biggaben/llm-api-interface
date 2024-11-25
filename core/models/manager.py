# core/models/manager.py
from typing import Dict, Optional
import logging
from datetime import datetime
from .config import ModelType, ModelConfig

class ModelManager:
    def __init__(self):
        self._models: Dict[ModelType, ModelConfig] = {
            ModelType.GPT4O: ModelConfig(
                model_type=ModelType.GPT4O,
                cost_per_1k_input_tokens=0.01,
                cost_per_1k_output_tokens=0.03,
                max_tokens=128000,
                context_window=128000,
                capabilities=["complex_reasoning", "code", "analysis"],
                typical_latency=2.0
            ),
            ModelType.O1_PREVIEW: ModelConfig(
                model_type=ModelType.O1_PREVIEW,
                cost_per_1k_input_tokens=0.01,
                cost_per_1k_output_tokens=0.03,
                max_tokens=128000,
                context_window=128000,
                capabilities=["complex_reasoning", "code", "analysis"],
                typical_latency=1.5
            ),
            ModelType.CLAUDE: ModelConfig(
                model_type=ModelType.CLAUDE,
                cost_per_1k_input_tokens=0.015,
                cost_per_1k_output_tokens=0.075,
                max_tokens=200000,
                context_window=200000,
                capabilities=["complex_reasoning", "code", "analysis"],
                typical_latency=3.0
            )
        }
        self._usage_metrics = {}
        self.logger = logging.getLogger(__name__)

    async def select_model(
        self,
        task_type: str,
        input_length: int,
        priority: str = "balanced",
        budget: Optional[float] = None,
    ) -> ModelType:
        """Select optimal model based on requirements."""
        try:
            self.logger.info(f"Selecting model for task: {task_type}, length: {input_length}, priority: {priority}")
            
            # For budget-conscious tasks
            if budget is not None:
                if budget < 0.02:  # Low budget
                    return ModelType.GPT4O
                elif budget < 0.05:  # Medium budget
                    return ModelType.CLAUDE
                else:  # High budget
                    if task_type in ["cot", "complex_reasoning", "analysis"]:
                        return ModelType.O1_PREVIEW
            
            # For chain of thought and complex reasoning (with sufficient budget)
            if task_type in ["cot", "complex_reasoning", "analysis"]:
                return ModelType.O1_PREVIEW
            
            # For very long inputs, prefer Claude due to context window
            if input_length > 100000:
                return ModelType.CLAUDE
            
            # For code generation
            if task_type == "code":
                return ModelType.GPT4O
            
            # For creative tasks
            if task_type in ["creative", "writing"]:
                return ModelType.CLAUDE
            
            # For speed-priority tasks
            if priority == "speed":
                return ModelType.GPT4O

            # Default to GPT4O for balanced performance
            return ModelType.GPT4O

        except Exception as e:
            self.logger.error(f"Model selection error: {e}")
            # Default to GPT4O as fallback
            return ModelType.GPT4O

    def calculate_cost(
        self,
        model: ModelType,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost for a model run."""
        config = self._models[model]
        input_cost = (input_tokens / 1000) * config.cost_per_1k_input_tokens
        output_cost = (output_tokens / 1000) * config.cost_per_1k_output_tokens
        return input_cost + output_cost

    def get_model_config(self, model_type: ModelType) -> ModelConfig:
        """Get model configuration."""
        return self._models[model_type]

    def log_usage(self, model: ModelType, input_tokens: int, output_tokens: int):
        """Log model usage metrics."""
        cost = self.calculate_cost(model, input_tokens, output_tokens)
        self._usage_metrics.setdefault(model, {
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'total_cost': 0.0,
            'calls': 0
        })
        
        metrics = self._usage_metrics[model]
        metrics['total_input_tokens'] += input_tokens
        metrics['total_output_tokens'] += output_tokens
        metrics['total_cost'] += cost
        metrics['calls'] += 1

    def get_metrics(self) -> Dict:
        """Get current usage metrics."""
        return self._usage_metrics.copy()