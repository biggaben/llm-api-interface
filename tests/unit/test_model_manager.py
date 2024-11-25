# tests/unit/test_model_manager.py
import pytest
from core.models.manager import ModelManager
from core.models.config import ModelType

@pytest.fixture
def model_manager():
    return ModelManager()

@pytest.mark.asyncio
class TestModelSelection:
    async def test_reasoning_tasks_high_budget(self, model_manager):
        """Test that reasoning tasks use O1_PREVIEW with high budget"""
        tasks = ["cot", "complex_reasoning", "analysis"]
        for task in tasks:
            model = await model_manager.select_model(task, input_length=1000, budget=0.1)
            assert model == ModelType.O1_PREVIEW, f"Expected O1_PREVIEW for {task} task with high budget"

    async def test_reasoning_tasks_low_budget(self, model_manager):
        """Test that reasoning tasks fallback to other models with low budget"""
        model = await model_manager.select_model("analysis", input_length=1000, budget=0.01)
        assert model == ModelType.GPT4O, "Expected GPT4O for analysis task with low budget"

    async def test_code_tasks(self, model_manager):
        """Test that code tasks use GPT4O"""
        model = await model_manager.select_model("code", input_length=1000)
        assert model == ModelType.GPT4O

    async def test_creative_tasks(self, model_manager):
        """Test that creative tasks use Claude"""
        tasks = ["creative", "writing"]
        for task in tasks:
            model = await model_manager.select_model(task, input_length=1000)
            assert model == ModelType.CLAUDE, f"Expected CLAUDE for {task} task"

    async def test_long_input(self, model_manager):
        """Test that very long inputs use Claude"""
        model = await model_manager.select_model("chat", input_length=150000)
        assert model == ModelType.CLAUDE

    async def test_speed_priority(self, model_manager):
        """Test that speed priority uses GPT4O"""
        model = await model_manager.select_model(
            "chat", 
            input_length=1000, 
            priority="speed"
        )
        assert model == ModelType.GPT4O

    async def test_budget_constraints(self, model_manager):
        """Test budget-based model selection"""
        # Low budget
        model = await model_manager.select_model(
            "chat", 
            input_length=1000, 
            budget=0.01
        )
        assert model == ModelType.GPT4O

        # Medium budget
        model = await model_manager.select_model(
            "chat", 
            input_length=1000, 
            budget=0.03
        )
        assert model == ModelType.CLAUDE

        # High budget
        model = await model_manager.select_model(
            "analysis", 
            input_length=1000, 
            budget=0.06
        )
        assert model == ModelType.O1_PREVIEW

    async def test_default_selection(self, model_manager):
        """Test default model selection"""
        model = await model_manager.select_model("chat", input_length=1000)
        assert model == ModelType.GPT4O

def test_cost_calculation(model_manager):
    """Test cost calculation"""
    test_cases = [
        (ModelType.CLAUDE, 1000, 500),
        (ModelType.GPT4O, 1000, 500),
        (ModelType.O1_PREVIEW, 1000, 500)
    ]
    
    for model_type, input_tokens, output_tokens in test_cases:
        cost = model_manager.calculate_cost(
            model_type,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )
        assert cost >= 0, f"Cost should be non-negative for {model_type}"
        assert isinstance(cost, float), f"Cost should be float for {model_type}"