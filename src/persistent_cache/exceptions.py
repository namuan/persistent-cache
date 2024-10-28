class CacheError(Exception):
    """Base exception for cache-related errors."""


class CacheCorruptionError(CacheError):
    """Raised when a cache file is corrupted"""


class SerializationError(CacheError):
    """Raised when serialization or deserialization fails."""
