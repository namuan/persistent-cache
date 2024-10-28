import importlib
import inspect
from dataclasses import asdict
from dataclasses import is_dataclass
from typing import Any
from typing import Set

from persistent_cache.exceptions import SerializationError


class ObjectSerializer:
    @staticmethod
    def serialize(obj: Any, seen: Set = None) -> Any:
        if seen is None:
            seen = set()

        # Handle circular references
        obj_id = id(obj)
        if obj_id in seen:
            return f"<Circular reference to {obj.__class__.__name__}>"

        if obj is None or isinstance(obj, (int, float, str, bool)):
            return obj

        # Add object to seen set for circular reference detection
        seen.add(obj_id)

        try:
            if is_dataclass(obj):
                return {
                    "__dataclass__": obj.__class__.__name__,
                    "module": obj.__class__.__module__,
                    "data": asdict(obj),
                }

            if isinstance(obj, (list, tuple)):
                return [ObjectSerializer.serialize(item, seen) for item in obj]

            if isinstance(obj, dict):
                return {
                    ObjectSerializer.serialize(k, seen): ObjectSerializer.serialize(
                        v, seen
                    )
                    for k, v in obj.items()
                }

            if inspect.isfunction(obj):
                raise SerializationError("Functions cannot be serialized")

            if hasattr(obj, "__dict__"):
                return {
                    "__class__": obj.__class__.__name__,
                    "module": obj.__class__.__module__,
                    "attributes": ObjectSerializer.serialize(obj.__dict__, seen),
                }

            raise SerializationError(f"Unable to serialize object of type {type(obj)}")

        finally:
            # Remove object from seen set when we're done with it
            seen.discard(obj_id)

    @staticmethod
    def deserialize(obj: Any) -> Any:
        if obj is None or isinstance(obj, (int, float, str, bool)):
            return obj

        if isinstance(obj, str) and obj.startswith("<Circular reference to"):
            return obj

        if isinstance(obj, dict):
            if "__dataclass__" in obj:
                module_name = obj["module"]
                class_name = obj["__dataclass__"]
                try:
                    module = importlib.import_module(module_name)
                    cls = getattr(module, class_name)
                    return cls(**obj["data"])
                except (ImportError, AttributeError) as e:
                    raise SerializationError(f"Failed to deserialize dataclass: {e}")

            if "__class__" in obj:
                module_name = obj["module"]
                class_name = obj["__class__"]
                try:
                    module = importlib.import_module(module_name)
                    cls = getattr(module, class_name)
                    instance = cls.__new__(cls)
                    instance.__dict__.update(
                        ObjectSerializer.deserialize(obj["attributes"])
                    )
                    return instance
                except (ImportError, AttributeError) as e:
                    raise SerializationError(f"Failed to deserialize class: {e}")

            return {
                ObjectSerializer.deserialize(k): ObjectSerializer.deserialize(v)
                for k, v in obj.items()
            }

        if isinstance(obj, (list, tuple)):
            return [ObjectSerializer.deserialize(item) for item in obj]

        return obj
