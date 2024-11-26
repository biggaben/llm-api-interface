# tests/unit/test_settings.py
import pytest
from pathlib import Path
import os
from config.settings import Settings, get_settings

def test_settings_defaults():
    settings = Settings()
    assert settings.project_name == "llm-api-interface"
    assert settings.debug is False
    assert settings.api_timeout == 30
    assert settings.max_retries == 3
    assert isinstance(settings.cache_dir, Path)

def test_settings_env_override(monkeypatch):
    # Set environment variables
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("API_TIMEOUT", "60")
    
    settings = Settings()
    assert settings.anthropic_api_key == "test-anthropic-key"
    assert settings.openai_api_key == "test-openai-key"
    assert settings.debug is True
    assert settings.api_timeout == 60

def test_settings_cache():
    # Test that get_settings uses cache
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2  # Same instance due to LRU cache

def test_settings_paths():
    settings = Settings()
    assert settings.base_dir.is_dir()
    assert settings.cache_dir.is_dir()  # Should be created in __init__

def test_settings_model_config():
    settings = Settings()
    assert settings.model_config["env_file"] == ".env"
    assert settings.model_config["case_sensitive"] is True
    assert settings.model_config["env_prefix"] == ""

def test_settings_logging_config():
    settings = Settings()
    assert settings.log_level == "INFO"
    assert "%(asctime)s" in settings.log_format
    assert "%(levelname)s" in settings.log_format