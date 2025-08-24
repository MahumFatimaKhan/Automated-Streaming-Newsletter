import time
import hashlib
import json
import os
from typing import Any, Optional
from config import Config

class SimpleCache:
    """Simple file-based cache implementation."""
    
    def __init__(self, cache_dir: str = None):
        self.cache_dir = cache_dir or os.path.join(Config.TEMP_FOLDER, 'cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        self.default_timeout = Config.CACHE_DEFAULT_TIMEOUT
    
    def _get_cache_key(self, key: str) -> str:
        """Generate cache file path from key."""
        # Hash the key to create a valid filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.cache")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        cache_file = self._get_cache_key(key)
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache has expired
            if cache_data['expiry'] < time.time():
                os.remove(cache_file)
                return None
            
            return cache_data['value']
            
        except (json.JSONDecodeError, KeyError, IOError):
            # Invalid cache file, remove it
            if os.path.exists(cache_file):
                os.remove(cache_file)
            return None
    
    def set(self, key: str, value: Any, timeout: int = None) -> None:
        """Set value in cache with optional timeout."""
        cache_file = self._get_cache_key(key)
        timeout = timeout or self.default_timeout
        
        cache_data = {
            'value': value,
            'expiry': time.time() + timeout,
            'created': time.time()
        }
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
        except IOError:
            # Silently fail if can't write cache
            pass
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        cache_file = self._get_cache_key(key)
        if os.path.exists(cache_file):
            os.remove(cache_file)
    
    def clear(self) -> None:
        """Clear all cache files."""
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.cache'):
                os.remove(os.path.join(self.cache_dir, filename))
    
    def cleanup_expired(self) -> None:
        """Remove expired cache files."""
        current_time = time.time()
        
        for filename in os.listdir(self.cache_dir):
            if not filename.endswith('.cache'):
                continue
            
            filepath = os.path.join(self.cache_dir, filename)
            
            try:
                with open(filepath, 'r') as f:
                    cache_data = json.load(f)
                
                if cache_data.get('expiry', 0) < current_time:
                    os.remove(filepath)
                    
            except (json.JSONDecodeError, KeyError, IOError):
                # Invalid cache file, remove it
                os.remove(filepath)


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, max_calls: int, period: int):
        self.max_calls = max_calls
        self.period = period  # in seconds
        self.calls = []
    
    def is_allowed(self) -> bool:
        """Check if a new call is allowed."""
        now = time.time()
        
        # Remove old calls outside the period
        self.calls = [call_time for call_time in self.calls 
                     if now - call_time < self.period]
        
        # Check if we can make a new call
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        
        return False
    
    def wait_time(self) -> float:
        """Get time to wait before next call is allowed."""
        if len(self.calls) < self.max_calls:
            return 0
        
        now = time.time()
        oldest_call = min(self.calls)
        wait = self.period - (now - oldest_call)
        
        return max(0, wait)