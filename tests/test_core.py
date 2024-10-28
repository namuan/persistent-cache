import os

import pytest
from persistent_cache.core import PersistentCache
from persistent_cache.exceptions import CacheCorruptionError
from persistent_cache.exceptions import CacheError


def test_basic_caching(cache_decorator):
    call_count = 0

    @cache_decorator
    def test_func(x, y):
        nonlocal call_count
        call_count += 1
        return x + y

    # First call
    result1 = test_func(1, 2)
    assert result1 == 3
    assert call_count == 1

    # Second call (should use cache)
    result2 = test_func(1, 2)
    assert result2 == 3
    assert call_count == 1  # Should not increase


def test_different_args(cache_decorator):
    call_count = 0

    @cache_decorator
    def test_func(x, y):
        nonlocal call_count
        call_count += 1
        return x + y

    result1 = test_func(1, 2)
    result2 = test_func(2, 3)

    assert call_count == 2  # Different args should cause new computation
    assert result1 == 3
    assert result2 == 5


def test_with_dataclass(cache_decorator, test_data):
    call_count = 0

    @cache_decorator
    def process_data(data):
        nonlocal call_count
        call_count += 1
        return f"{data.name}: {data.value}"

    # First call
    result1 = process_data(test_data)
    assert result1 == "test: 42"
    assert call_count == 1

    # Second call with same data
    result2 = process_data(test_data)
    assert result2 == "test: 42"
    assert call_count == 1  # Should use cache


def test_with_complex_args(cache_decorator, test_data):
    @cache_decorator
    def complex_func(lst: list, dct: dict, data):
        return len(lst) + len(dct) + data.value

    args = ([1, 2, 3], {"a": 1, "b": 2}, test_data)

    result1 = complex_func(*args)
    result2 = complex_func(*args)

    assert result1 == result2
    assert result1 == 47  # 3 (list) + 2 (dict) + 42 (TestData.value)


def test_cache_persistence(cache_dir):
    cache = PersistentCache(cache_dir=cache_dir)

    @cache
    def test_func(x):
        return x * 2

    # First call
    result1 = test_func(5)

    # Create new cache instance
    cache2 = PersistentCache(cache_dir=cache_dir)

    @cache2
    def test_func(x):
        return x * 3  # Different implementation

    # Should still return cached result
    result2 = test_func(5)

    assert result1 == result2 == 10


def test_invalid_cache_dir(tmp_path):
    # Create a file that will conflict with cache directory
    dummy_file = tmp_path / "dummy_file"
    dummy_file.write_text("test")

    # Attempt to create cache with path that exists as a file
    with pytest.raises(ValueError) as exc_info:
        PersistentCache(cache_dir=str(dummy_file))

    assert "Cannot create cache directory" in str(exc_info.value)


def test_valid_cache_dir(tmp_path):
    cache_dir = tmp_path / "cache"
    PersistentCache(cache_dir=str(cache_dir))
    assert os.path.exists(str(cache_dir))


def test_non_serializable_args(cache_decorator):
    @cache_decorator
    def test_func(x):
        return x

    # Try to cache a function (which isn't serializable by default)
    def some_func():
        pass

    with pytest.raises(CacheError):
        test_func(some_func)


def test_cache_file_corruption(tmp_path):
    # Setup
    cache_dir = tmp_path / "cache"
    cache = PersistentCache(cache_dir=str(cache_dir))

    # Create a corrupted cache file
    cache_key = "test_func_123"
    corrupted_cache_path = cache._get_cache_path(cache_key)
    os.makedirs(os.path.dirname(corrupted_cache_path), exist_ok=True)

    with open(corrupted_cache_path, "w") as f:
        f.write('{"corrupted": "json"')  # Intentionally malformed JSON

    # Test corrupted cache handling
    with pytest.raises(CacheCorruptionError) as exc_info:
        cache.get(cache_key)

    # Verify the corrupted file is removed
    assert not os.path.exists(corrupted_cache_path)
    assert "Corrupted cache file" in str(exc_info.value)


def test_cache_recovery_after_corruption(tmp_path):
    cache_dir = tmp_path / "cache"
    cache = PersistentCache(cache_dir=str(cache_dir))

    @cache
    def test_func(x):
        return x * 2

    # First call - cache the result
    result1 = test_func(5)

    # Corrupt the cache file
    cache_files = [f for f in os.listdir(str(cache_dir)) if f.startswith("test_func_")]
    cache_file = os.path.join(str(cache_dir), cache_files[0])
    with open(cache_file, "w") as f:
        f.write('{"corrupted": "json"')

    # Second call - should handle corruption and recalculate
    result2 = test_func(5)

    assert result1 == result2 == 10
