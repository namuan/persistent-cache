import os
import time
from dataclasses import dataclass

from persistent_cache.core import PersistentCache

# Custom cache directory
CACHE_DIR = ".my_cache"
cache = PersistentCache(cache_dir=CACHE_DIR)


@dataclass
class UserData:
    id: int
    name: str
    age: int


# Complex input types
@cache
def process_user_data(user: UserData, settings: dict) -> str:
    """Process user data with settings"""
    time.sleep(1)  # Simulate processing
    return f"Processed {user.name}'s data with {len(settings)} settings"


# Function with multiple complex arguments
@cache
def analyze_users(users: list[UserData], params: dict, threshold: float) -> dict:
    """Analyze multiple users with parameters"""
    time.sleep(2)  # Simulate analysis
    return {
        "total_users": len(users),
        "avg_age": sum(user.age for user in users) / len(users),
        "threshold_applied": threshold,
        "params_used": params,
    }


def demonstrate_dataclass_caching():
    print("Dataclass Caching Example")
    print("=" * 50)

    user = UserData(id=1, name="Alice", age=30)
    settings = {"verbose": True, "mode": "fast"}

    print("First call with dataclass...")
    start = time.time()
    result1 = process_user_data(user, settings)
    duration1 = time.time() - start
    print(f"Result: {result1}")
    print(f"Duration: {duration1:.2f}s")

    print("\nSecond call (cached)...")
    start = time.time()
    result2 = process_user_data(user, settings)
    duration2 = time.time() - start
    print(f"Result: {result2}")
    print(f"Duration: {duration2:.2f}s")


def demonstrate_complex_caching():
    print("\nComplex Arguments Example")
    print("=" * 50)

    users = [
        UserData(id=1, name="Alice", age=30),
        UserData(id=2, name="Bob", age=25),
        UserData(id=3, name="Charlie", age=35),
    ]
    params = {
        "method": "advanced",
        "filters": ["age", "name"],
        "options": {"sort": True},
    }
    threshold = 0.75

    print("First analysis...")
    start = time.time()
    result1 = analyze_users(users, params, threshold)
    duration1 = time.time() - start
    print(f"Result: {result1}")
    print(f"Duration: {duration1:.2f}s")

    print("\nSecond analysis (cached)...")
    start = time.time()
    result2 = analyze_users(users, params, threshold)
    duration2 = time.time() - start
    print(f"Result: {result2}")
    print(f"Duration: {duration2:.2f}s")


def demonstrate_cache_management():
    print("\nCache Management Example")
    print("=" * 50)

    # Clear specific cache entries
    cache.clear("process_user_data")
    print("Cleared cache for process_user_data")

    # Clear all cache
    cache.clear_all()
    print("Cleared all cache")

    # Cache size
    cache_size = sum(
        os.path.getsize(os.path.join(CACHE_DIR, f))
        for f in os.listdir(CACHE_DIR)
        if os.path.isfile(os.path.join(CACHE_DIR, f))
    )
    print(f"Current cache size: {cache_size / 1024:.2f} KB")


if __name__ == "__main__":
    demonstrate_dataclass_caching()
    demonstrate_complex_caching()
    demonstrate_cache_management()
