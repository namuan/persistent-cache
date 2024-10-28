# Persistent Cache

A Python package that provides persistent function result caching with support for complex data types, including classes and dataclasses.

## Features

- 🚀 Simple decorator-based implementation
- 💾 Persistent caching across program restarts
- 🔄 Automatic serialization of complex data types
- 📦 Support for:
    - Basic types (int, float, str, bool)
    - Collections (lists, tuples, dictionaries)
    - Dataclasses
    - Custom classes
    - Nested data structures
- 🔒 Thread-safe file operations
- 📁 Customizable cache directory
- ⚡ Efficient hashing of function arguments
- 🐛 Comprehensive error handling

## Installation

```shell
python3 -m pip install git+https://github.com/namuan/persistent-cache
```

## Quick Start

### Basic Usage

```python
from persistent_cache.core import PersistentCache

@PersistentCache()
def expensive_calculation(x: int, y: int) -> int:
    print("Computing...")
    return x + y

# First call - will compute
result1 = expensive_calculation(1, 2)  # Prints: Computing...

# Second call - will use cache
result2 = expensive_calculation(1, 2)  # No printing, returns cached result
```

**With Dataclasses**

```python
from dataclasses import dataclass
from persistent_cache.core import PersistentCache

@dataclass
class Point:
    x: float
    y: float

@PersistentCache()
def calculate_distance(point: Point) -> float:
    print("Calculating distance...")
    return (point.x ** 2 + point.y ** 2) ** 0.5

# First call
distance1 = calculate_distance(Point(3.0, 4.0))  # Prints: Calculating distance...

# Second call with same values
distance2 = calculate_distance(Point(3.0, 4.0))  # Uses cache
```

**With Custom Classes**

```python
from persistent_cache.core import PersistentCache

class Rectangle:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

@PersistentCache()
def calculate_area(rect: Rectangle) -> float:
    print("Calculating area...")
    return rect.width * rect.height

# First call
area1 = calculate_area(Rectangle(5.0, 6.0))  # Prints: Calculating area...

# Second call with same values
area2 = calculate_area(Rectangle(5.0, 6.0))  # Uses cache
```

### Advanced Usage

**Custom Cache Directory**

```python
@PersistentCache(cache_dir='my_cache')
def my_function():
    pass
```

**Complex Arguments**

```python
@PersistentCache()
def process_data(
    numbers: list,
    options: dict,
    point: Point,
    config: dict = None
) -> dict:
    # Process data...
    pass

result = process_data(
    numbers=[1, 2, 3],
    options={'precision': 0.001},
    point=Point(1.0, 2.0),
    config={'max_iterations': 100}
)
```

**Error Handling**

```python
from persistent_cache.exceptions import CacheError, SerializationError

try:
    @PersistentCache()
    def risky_function(data):
        # Some risky operation
        pass

except SerializationError as e:
    print(f"Failed to serialize arguments: {e}")
except CacheError as e:
    print(f"Cache operation failed: {e}")
```

## Performance Considerations

Cache files are stored per function
Arguments are hashed using MD5 for quick lookup
Large arguments may impact serialization performance
Cache files grow as more unique argument combinations are used

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

### Fork the repository
Create your feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request

## Development Setup

```shell
# Clone the repository
git clone https://github.com/namuan/persistent-cache.git
cd persistent-cache

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements/requirements-dev.txt
```

## Testing

### Run all tests
```shell
./venv/bin/pytest
```

### Run specific test file
```shell
./venv/bin/pytest tests/test_core.py
```

### Run with verbose output
```shell
./venv/bin/pytest -v
```

# Run with coverage report
```shell
./venv/bin/pytest --cov=persistent_cache --cov-report=html
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Support
If you encounter any problems or have suggestions, please open an issue.
