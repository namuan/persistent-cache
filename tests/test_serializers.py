from dataclasses import dataclass
from datetime import datetime
from datetime import timezone

import pytest
from persistent_cache.exceptions import SerializationError
from persistent_cache.serializers import ObjectSerializer


@dataclass
class SimpleData:
    value: int
    name: str


def test_primitive_serialization():
    assert ObjectSerializer.serialize(42) == 42
    assert ObjectSerializer.serialize("test") == "test"
    assert ObjectSerializer.serialize(True) is True
    assert ObjectSerializer.serialize(None) is None
    assert ObjectSerializer.serialize(3.14) == 3.14


def test_list_serialization():
    data = [1, "test", True]
    serialized = ObjectSerializer.serialize(data)
    assert serialized == data


def test_dict_serialization():
    data = {"a": 1, "b": "test", "c": True}
    serialized = ObjectSerializer.serialize(data)
    assert serialized == data


def test_nested_structure_serialization():
    data = {"list": [1, 2, 3], "dict": {"a": 1}, "mixed": [{"b": 2}]}
    serialized = ObjectSerializer.serialize(data)
    assert serialized == data


def test_dataclass_serialization():
    data = SimpleData(value=42, name="test")
    serialized = ObjectSerializer.serialize(data)

    assert isinstance(serialized, dict)
    assert serialized["__dataclass__"] == "SimpleData"
    assert serialized["data"] == {"value": 42, "name": "test"}
    assert serialized["module"] == "tests.test_serializers"


def test_dataclass_deserialization():
    data = SimpleData(value=42, name="test")
    serialized = ObjectSerializer.serialize(data)
    deserialized = ObjectSerializer.deserialize(serialized)

    assert isinstance(deserialized, SimpleData)
    assert deserialized.value == 42
    assert deserialized.name == "test"


def test_circular_reference():
    class CircularRef:
        def __init__(self):
            self.ref = self

        def __str__(self):
            return "CircularRef()"

    obj = CircularRef()
    serialized = ObjectSerializer.serialize(obj)

    def find_circular_ref(data):
        if isinstance(data, str) and data.startswith("<Circular reference to"):
            return True
        if isinstance(data, dict):
            return any(find_circular_ref(v) for v in data.values())
        if isinstance(data, (list, tuple)):
            return any(find_circular_ref(item) for item in data)
        return False

    assert find_circular_ref(
        serialized
    ), "No circular reference marker found in serialized data"


def test_function_serialization():
    def test_func():
        pass

    with pytest.raises(SerializationError):
        ObjectSerializer.serialize(test_func)


def test_complex_nested_structure():
    data = SimpleData(value=42, name="test")
    complex_data = {"data": data, "list": [data, {"nested": data}], "dict": {"a": data}}

    serialized = ObjectSerializer.serialize(complex_data)
    deserialized = ObjectSerializer.deserialize(serialized)

    assert isinstance(deserialized["data"], SimpleData)
    assert isinstance(deserialized["list"][0], SimpleData)
    assert isinstance(deserialized["list"][1]["nested"], SimpleData)
    assert isinstance(deserialized["dict"]["a"], SimpleData)


def test_datetime_serialization():
    # Test naive datetime
    naive_dt = datetime(2024, 1, 1, 12, 0, 0)
    serialized_naive = ObjectSerializer.serialize(naive_dt)
    deserialized_naive = ObjectSerializer.deserialize(serialized_naive)

    assert isinstance(deserialized_naive, datetime)
    assert deserialized_naive.year == 2024
    assert deserialized_naive.month == 1
    assert deserialized_naive.day == 1
    assert deserialized_naive.hour == 12
    assert deserialized_naive.minute == 0
    assert deserialized_naive.second == 0
    assert deserialized_naive.tzinfo is None

    # Test timezone-aware datetime
    aware_dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    serialized_aware = ObjectSerializer.serialize(aware_dt)
    deserialized_aware = ObjectSerializer.deserialize(serialized_aware)

    assert isinstance(deserialized_aware, datetime)
    assert deserialized_aware.year == 2024
    assert deserialized_aware.month == 1
    assert deserialized_aware.day == 1
    assert deserialized_aware.hour == 12
    assert deserialized_aware.minute == 0
    assert deserialized_aware.second == 0

    # Test datetime in complex structure
    complex_data = {
        "dt": naive_dt,
        "list": [aware_dt, naive_dt],
        "nested": {"dt": aware_dt},
    }

    serialized_complex = ObjectSerializer.serialize(complex_data)
    deserialized_complex = ObjectSerializer.deserialize(serialized_complex)

    assert isinstance(deserialized_complex["dt"], datetime)
    assert isinstance(deserialized_complex["list"][0], datetime)
    assert isinstance(deserialized_complex["list"][1], datetime)
    assert isinstance(deserialized_complex["nested"]["dt"], datetime)
