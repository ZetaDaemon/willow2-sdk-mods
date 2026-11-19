import unrealsdk
from unrealsdk.unreal import UObject, WeakPointer

_definition_cache: dict[str, WeakPointer[UObject]] = {}


def find_object(path: str) -> UObject:
    cached = _definition_cache.get(path)
    if cached is None or (obj := cached()) is None:
        obj = unrealsdk.find_object("Object", path)
        _definition_cache[path] = WeakPointer(obj)

    return obj
