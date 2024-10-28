import time

from persistent_cache.core import PersistentCache

# Initialize cache with default settings
cache = PersistentCache()


# Basic function caching
@cache
def expensive_computation(x: int, y: int) -> int:
    """Simulate an expensive computation"""
    time.sleep(2)  # Simulate long computation
    return x * y


def demonstrate_basic_caching():
    print("First call (will take ~2 seconds)...")
    start = time.time()
    result1 = expensive_computation(5, 3)
    duration1 = time.time() - start
    print(f"Result: {result1}, Duration: {duration1:.2f}s")

    print("\nSecond call (should be instant)...")
    start = time.time()
    result2 = expensive_computation(5, 3)
    duration2 = time.time() - start
    print(f"Result: {result2}, Duration: {duration2:.2f}s")


# Using cache with different arguments
def demonstrate_different_args():
    print("\nCalling with different arguments...")
    start = time.time()
    result = expensive_computation(10, 4)
    duration = time.time() - start
    print(f"Result: {result}, Duration: {duration:.2f}s")


if __name__ == "__main__":
    print("Basic Usage Example")
    print("=" * 50)
    demonstrate_basic_caching()
    demonstrate_different_args()
