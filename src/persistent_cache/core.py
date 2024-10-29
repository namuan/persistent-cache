import functools
import hashlib
import logging
import os
import pickle
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Optional


class PersistentCache:
    """
    A decorator class that provides persistent caching of function results.

    Features:
    - Persistent storage of function results
    - Automatic serialization of complex data types
    - Configurable cache directory
    - Efficient argument hashing
    - Comprehensive error handling
    """

    def __init__(
        self, cache_dir: Optional[str] = None, expiry_seconds: Optional[int] = None
    ):
        """
        Initialize the cache decorator.

        Args:
            cache_dir: Directory to store cache files. Defaults to '.cache'
            expiry_seconds: Cache expiry time in seconds. None means no expiry
        """
        self.cache_dir = Path(cache_dir or ".cache")
        self.expiry_seconds = expiry_seconds
        self._setup_cache_dir()

    def _setup_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist."""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logging.error(f"Failed to create cache directory: {e}")
            raise

    def _generate_key(self, func: Callable, args: tuple, kwargs: dict) -> str:
        """
        Generate a unique cache key based on function name and arguments.

        Returns:
            str: A hex digest of the hash
        """
        try:
            # Combine function name with stringified arguments
            key_parts = [func.__name__, str(args), str(sorted(kwargs.items()))]
            key_string = "|".join(key_parts)

            # Create an MD5 hash of the key string
            return hashlib.md5(key_string.encode()).hexdigest()
        except Exception as e:
            logging.error(f"Failed to generate cache key: {e}")
            raise

    def _get_cache_path(self, key: str) -> Path:
        """Get the full path for a cache file."""
        return self.cache_dir / f"{key}.pickle"

    def _save_to_cache(self, key: str, value: Any) -> None:
        """Save a value to the cache."""
        try:
            cache_path = self._get_cache_path(key)
            with open(cache_path, "wb") as f:
                pickle.dump(
                    {
                        "value": value,
                        "timestamp": os.time() if self.expiry_seconds else None,
                    },
                    f,
                )
        except Exception as e:
            logging.error(f"Failed to save to cache: {e}")
            raise

    def _load_from_cache(self, key: str) -> Optional[Any]:
        """Load a value from the cache if it exists and hasn't expired."""
        try:
            cache_path = self._get_cache_path(key)

            if not cache_path.exists():
                return None

            with open(cache_path, "rb") as f:
                cached_data = pickle.load(f)

            # Check expiration if applicable
            if self.expiry_seconds:
                if os.time() - cached_data["timestamp"] > self.expiry_seconds:
                    cache_path.unlink()  # Delete expired cache
                    return None

            return cached_data["value"]

        except Exception as e:
            logging.error(f"Failed to load from cache: {e}")
            return None

    def __call__(self, func: Callable) -> Callable:
        """
        Decorator implementation.

        Args:
            func: The function to cache

        Returns:
            Callable: Wrapped function with caching
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Generate cache key
                cache_key = self._generate_key(func, args, kwargs)

                # Try to load from cache
                cached_result = self._load_from_cache(cache_key)
                if cached_result is not None:
                    return cached_result

                # Calculate new result
                result = func(*args, **kwargs)

                # Save to cache
                self._save_to_cache(cache_key, result)

                return result

            except Exception as e:
                logging.error(f"Cache operation failed: {e}")
                # Fall back to original function
                return func(*args, **kwargs)

        return wrapper
