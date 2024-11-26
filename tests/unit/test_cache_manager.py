# tests/unit/test_cache_manager.py
import pytest
from pathlib import Path
import json
from datetime import datetime, timedelta
import time
from utils.cache.manager import CacheManager
from config.settings import Settings

@pytest.fixture
def mock_settings(monkeypatch):
    settings = Settings()
    monkeypatch.setattr(settings, "CACHE_ENABLED", True)
    monkeypatch.setattr(settings, "CACHE_TTL", 3600)
    return settings

@pytest.fixture
def temp_cache_dir(tmp_path):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir

@pytest.fixture
def cache_manager(temp_cache_dir, mock_settings):
    return CacheManager(cache_dir=temp_cache_dir, settings=mock_settings)

class TestCacheManager:
    def test_cache_key_generation(self, cache_manager):
        model = "test-model"
        messages = [{"role": "user", "content": "test"}]
        
        key1 = cache_manager._get_cache_key(model, messages)
        key2 = cache_manager._get_cache_key(model, messages)
        
        assert key1 == key2
        assert isinstance(key1, str)
        assert len(key1) > 0

    def test_cache_set_and_get(self, cache_manager, mock_settings):
        model = "test-model"
        messages = [{"role": "user", "content": "test"}]
        response = {"response": "test response"}
        
        # Verify cache is enabled
        assert cache_manager.settings.CACHE_ENABLED is True
        
        # Test set
        cache_manager.set(model, messages, response)
        
        # Test get
        cached = cache_manager.get(model, messages)
        assert cached == response

    def test_cache_expiration(self, cache_manager, mock_settings, monkeypatch):
        # Override cache TTL to 1 second for testing
        monkeypatch.setattr(mock_settings, "CACHE_TTL", 1)
        cache_manager.settings = mock_settings
        
        model = "test-model"
        messages = [{"role": "user", "content": "test"}]
        response = {"response": "test response"}
        
        # Set cache with current UTC time
        key = cache_manager._get_cache_key(model, messages)
        cache_path = cache_manager._get_cache_path(key)
        data = {
            "cached_at": datetime.utcnow().isoformat(),
            "model": model,
            "messages": messages,
            "response": response
        }
        cache_path.write_text(json.dumps(data))
        
        # Should be in cache
        assert cache_manager.get(model, messages) == response
        
        # Wait for expiration
        time.sleep(1.5)  # Increased sleep time for reliability
        
        # Should be expired
        assert cache_manager.get(model, messages) is None

    def test_cache_clear(self, cache_manager, mock_settings):
        model = "test-model"
        messages = [{"role": "user", "content": "test"}]
        response = {"response": "test response"}
        
        cache_manager.set(model, messages, response)
        assert cache_manager.get(model, messages) == response
        
        cache_manager.clear()
        assert cache_manager.get(model, messages) is None

    def test_cache_clear_with_age(self, cache_manager, mock_settings):
        model = "test-model"
        messages = [{"role": "user", "content": "test"}]
        response = {"response": "test response"}
        
        # Set cache entry with old timestamp
        key = cache_manager._get_cache_key(model, messages)
        cache_path = cache_manager._get_cache_path(key)
        old_time = datetime.utcnow() - timedelta(hours=2)
        
        data = {
            "cached_at": old_time.isoformat(),
            "model": model,
            "messages": messages,
            "response": response
        }
        
        cache_path.write_text(json.dumps(data))
        
        # Clear cache entries older than 1 hour
        cache_manager.clear(age_hours=1)
        
        # Old entry should be cleared
        assert cache_manager.get(model, messages) is None

    def test_cache_disabled(self, cache_manager, mock_settings, monkeypatch):
        # Disable cache
        monkeypatch.setattr(mock_settings, "CACHE_ENABLED", False)
        cache_manager.settings = mock_settings
        
        # Verify cache is disabled
        assert cache_manager.settings.CACHE_ENABLED is False
        
        model = "test-model"
        messages = [{"role": "user", "content": "test"}]
        response = {"response": "test response"}
        
        # Attempt to set cache
        cache_manager.set(model, messages, response)
        
        # Verify nothing was cached
        assert cache_manager.get(model, messages) is None
        
        # Verify cache file wasn't created
        key = cache_manager._get_cache_key(model, messages)
        cache_path = cache_manager._get_cache_path(key)
        assert not cache_path.exists()

    def test_invalid_cache_entry(self, cache_manager, mock_settings):
        model = "test-model"
        messages = [{"role": "user", "content": "test"}]
        
        # Write invalid JSON
        key = cache_manager._get_cache_key(model, messages)
        cache_path = cache_manager._get_cache_path(key)
        cache_path.write_text("invalid json")
        
        assert cache_manager.get(model, messages) is None

    def test_cache_settings_propagation(self, cache_manager, mock_settings):
        """Test that settings changes are properly propagated"""
        assert cache_manager.settings.CACHE_ENABLED is True
        assert cache_manager.settings.CACHE_TTL == 3600