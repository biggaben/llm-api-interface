# tests/unit/test_cli.py
import pytest
from typer.testing import CliRunner
from interfaces.cli.main import app
from core.models.config import ModelType

runner = CliRunner()

def test_list_models():
    result = runner.invoke(app, ["list-models"])
    assert result.exit_code == 0
    # Check for model truncated names to match rich table output
    assert "claude-3-5-sonnet" in result.stdout
    assert "gpt-4o" in result.stdout
    assert "o1-preview" in result.stdout

def test_cost_estimate():
    result = runner.invoke(app, [
        "cost-estimate",
        "-m", ModelType.CLAUDE.value,
        "-i", "1000",
        "-o", "500"
    ])
    assert result.exit_code == 0
    assert "$" in result.stdout
    assert "cost" in result.stdout.lower()

def test_cost_estimate_invalid_model():
    result = runner.invoke(app, [
        "cost-estimate",
        "-m", "invalid-model",
        "-i", "1000",
        "-o", "500"
    ])
    assert result.exit_code == 1
    assert "Invalid model" in result.stdout

@pytest.mark.asyncio
async def test_chat_invalid_model():
    result = runner.invoke(app, ["chat", "--model", "invalid-model"])
    assert result.exit_code == 0
    assert "Invalid model" in result.stdout
    assert "Available models" in result.stdout