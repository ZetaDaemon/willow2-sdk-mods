from abc import ABC, abstractmethod
from dataclasses import dataclass

import unrealsdk
from unrealsdk.unreal import UClass, UObject, WeakPointer


class ObjReference[T: UObject = UObject](ABC):
    """Reference to an object.

    Object is saved with a weak pointer after looking it up.
    """

    _obj_pointer: WeakPointer[T] | None = None

    @abstractmethod
    def get_object(self) -> T:
        """Get the object being referenced.

        Subclasses must implement this method.
        """

    def __call__(self) -> T:
        """Get the UObject."""
        if self._obj_pointer is None or (obj := self._obj_pointer()) is None:
            obj = self.get_object()
            self._obj_pointer = WeakPointer(obj)
        return obj


@dataclass
class ObjReferenceByName[T: UObject = UObject](ObjReference[T]):
    """Reference to an object by name."""

    cls: UClass | str
    name: str

    def get_object(self) -> T:
        """Get the object using find_object."""
        return unrealsdk.find_object(self.cls, self.name)


@dataclass
class ObjReferenceConstructed[T: UObject = UObject](ObjReference[T]):
    """Reference to an object that should be constructed."""

    cls: UClass | str
    outer: ObjReference | None = None
    name: str = "None"
    flags: int = 0
    template: ObjReference | None = None

    def get_object(self) -> T:
        """Construct the object."""
        return unrealsdk.construct_object(
            self.cls,
            None if self.outer is None else self.outer(),
            self.name,
            self.flags,
            None if self.template is None else self.template(),
        )


def register_submodule() -> None:
    return None
