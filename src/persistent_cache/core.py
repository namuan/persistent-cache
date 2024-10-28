# src/persistent_cache/cache.py
import hashlib
import json
import os
from functools import wraps
from typing import Any
from typing import Callable
from typing import Optional

from .exceptions import CacheCorruptionError
from .exceptions import CacheError
from .serializers import ObjectSerializer


class PersistentCache:
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = cache_dir
        self._init_cache_dir()

    def _init_cache_dir(self) -> None:
        """Initialize cache directory with proper validation"""
        if os.path.exists(self.cache_dir):
            if not os.path.isdir(self.cache_dir):
                raise ValueError(
                    f"Cannot create cache directory: '{self.cache_dir}' exists and is not a directory"
                )
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
        except OSError as e:
            raise ValueError(
                f"Cannot create cache directory '{self.cache_dir}': {str(e)}"
            )

    def _get_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate a unique cache key based on function name and arguments"""
        serialized_args = ObjectSerializer.serialize((args, kwargs))
        args_hash = hashlib.md5(json.dumps(serialized_args).encode()).hexdigest()
        return f"{func_name}_{args_hash}"

    def _get_cache_path(self, cache_key: str) -> str:
        """Get the full path for a cache file"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")

    def get(self, cache_key: str) -> Optional[Any]:
        """Retrieve a value from cache"""
        cache_path = self._get_cache_path(cache_key)
        if os.path.exists(cache_path):
            try:
                with open(cache_path) as f:
                    serialized_data = json.load(f)
                    return ObjectSerializer.deserialize(serialized_data)
            except (
                json.JSONDecodeError,
                ValueError,
                TypeError,
                KeyError,
                IndexError,
            ) as e:
                # Remove corrupted cache file
                try:
                    os.remove(cache_path)
                except OSError:
                    pass  # Ignore deletion errors
                raise CacheCorruptionError(
                    f"Corrupted cache file {cache_path}: {str(e)}"
                )
        return None

    def set(self, cache_key: str, value: Any) -> None:
        """Store a value in cache"""
        cache_path = self._get_cache_path(cache_key)
        try:
            serialized_data = ObjectSerializer.serialize(value)
            with open(cache_path, "w") as f:
                json.dump(serialized_data, f)
        except (TypeError, ValueError, OSError) as e:
            raise CacheError(f"Failed to write cache file {cache_path}: {str(e)}")

    def clear(self, func_name: str) -> None:
        """Clear cache entries for a specific function"""
        for filename in os.listdir(self.cache_dir):
            if filename.startswith(f"{func_name}_"):
                try:
                    os.remove(os.path.join(self.cache_dir, filename))
                except OSError:
                    pass  # Ignore deletion errors

    def clear_all(self) -> None:
        """Clear all cache entries"""
        for filename in os.listdir(self.cache_dir):
            if filename.endswith(".json"):
                try:
                    os.remove(os.path.join(self.cache_dir, filename))
                except OSError:
                    pass  # Ignore deletion errors

    def get_size(self) -> int:
        """Get total size of cache in bytes"""
        total_size = 0
        for filename in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, filename)
            if os.path.isfile(file_path):
                try:
                    total_size += os.path.getsize(file_path)
                except OSError:
                    pass  # Ignore file access errors
        return total_size

    def __call__(self, func: Callable) -> Callable:
        """Decorator for caching function results"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = self._get_cache_key(func.__name__, args, kwargs)
            try:
                result = self.get(cache_key)
                if result is not None:
                    return result
            except CacheCorruptionError:
                pass  # Proceed to recalculate on corruption

            result = func(*args, **kwargs)
            try:
                self.set(cache_key, result)
            except CacheError:
                pass  # Ignore cache writing errors

            return result

        return wrapper
