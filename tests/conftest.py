import os
import shutil
from dataclasses import dataclass

import pytest
from persistent_cache.core import PersistentCache


@dataclass
class TestData:
    value: int
    name: str


@pytest.fixture
def test_data():
    """Fixture to provide test data instances"""
    return TestData(value=42, name="test")


@pytest.fixture
def cache_dir():
    """Fixture to provide a temporary cache directory"""
    test_cache_dir = ".test_cache"
    os.makedirs(test_cache_dir, exist_ok=True)
    yield test_cache_dir
    # Cleanup after tests
    shutil.rmtree(test_cache_dir)


@pytest.fixture
def cache_decorator(cache_dir):
    """Fixture to provide a PersistentCache instance"""
    return PersistentCache(cache_dir=cache_dir)
