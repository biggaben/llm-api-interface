# utils/cache/manager.py
import json
import hashlib
from pathlib import Path
from typing import Optional, Any, Dict
from datetime import datetime, timedelta, timezone

class CacheManager:
    """Manage caching of API responses."""
    
    def __init__(self, cache_dir: Optional[Path] = None, settings=None):
        from config.settings import settings as default_settings
        self.settings = settings or default_settings
        self.cache_dir = cache_dir or self.settings.cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, model: str, messages: list) -> str:
        """Generate a unique cache key for the request."""
        data = {
            "model": model,
            "messages": messages
        }
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for a key."""
        return self.cache_dir / f"{key}.json"
    
    def get(self, model: str, messages: list) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired."""
        if not getattr(self.settings, "CACHE_ENABLED", True):
            return None
            
        key = self._get_cache_key(model, messages)
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
            
        try:
            data = json.loads(cache_path.read_text())
            cached_time = datetime.fromisoformat(data["cached_at"])
            
            # Compare with current UTC time
            if cached_time + timedelta(seconds=self.settings.CACHE_TTL) < datetime.now(timezone.utc):
                cache_path.unlink()  # Remove expired cache
                return None
                
            return data["response"]
        except (json.JSONDecodeError, KeyError, TypeError):
            return None
    
    def set(self, model: str, messages: list, response: Dict[str, Any]):
        """Cache a response."""
        if not getattr(self.settings, "CACHE_ENABLED", True):
            return
            
        key = self._get_cache_key(model, messages)
        cache_path = self._get_cache_path(key)
        
        data = {
            "cached_at": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "messages": messages,
            "response": response
        }
        
        cache_path.write_text(json.dumps(data, indent=2))
    
    def clear(self, age_hours: Optional[int] = None):
        """Clear cache, optionally only entries older than age_hours."""
        if age_hours is not None:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=age_hours)
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    data = json.loads(cache_file.read_text())
                    cached_time = datetime.fromisoformat(data["cached_at"])
                    if cached_time < cutoff:
                        cache_file.unlink()
                except (json.JSONDecodeError, KeyError, TypeError):
                    cache_file.unlink()
        else:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()