# Thanks to juso's uemath lib for the numbers and maths on this.
# https://github.com/juso40/bl2sdk-mods/blob/main/uemath/umath.py
# I reimplemented stuff to work only with the structs, rather than the old tuples.
from __future__ import annotations

import math
from math import sqrt
from typing import TYPE_CHECKING, Self, cast, overload

import unrealsdk

if TYPE_CHECKING:
    from bl2.Core import Object


URU_180 = 32768
URU_TO_RADIANS = math.pi / URU_180
RADIANS_TO_URU = URU_180 / math.pi

VECTOR_SCRIPT_STRUCT = unrealsdk.find_object("ScriptStruct", "Core.Object:Vector")
ROTATOR_SCRIPT_STRUCT = unrealsdk.find_object("ScriptStruct", "Core.Object:Rotator")


class Vector:
    """Wrapper around Object.Vector to provide the math functions."""

    _wrapped_struct: Object.Vector

    @overload
    def __init__(self, struct: Object.Vector | Object.Rotator | Rotator | None = None) -> None: ...
    @overload
    def __init__(self, *, x: float = 0, y: float = 0, z: float = 0) -> None: ...
    def __init__(
        self,
        struct: Object.Vector | Object.Rotator | Rotator | None = None,
        *,
        x: float = 0,
        y: float = 0,
        z: float = 0,
    ) -> None:
        """Initialise a Vector.

        Can be initialized from either an Object.Vector, Object.Rotator, uemath.Rotator,
        or individual x, y, z values.
        """
        if struct is not None:
            if isinstance(struct, Rotator):
                self._wrapped_struct = Rotator.to_vector(struct.wrapped_struct)
            elif struct._type == VECTOR_SCRIPT_STRUCT:
                self._wrapped_struct = cast("Object.Vector", struct)
            elif struct._type == ROTATOR_SCRIPT_STRUCT:
                self._wrapped_struct = Rotator.to_vector(cast("Object.Rotator", struct))
            return
        self._wrapped_struct = cast("Object.Vector", unrealsdk.make_struct("Vector", X=x, Y=y, Z=z))

    @property
    def wrapped_struct(self) -> Object.Vector:
        return self._wrapped_struct

    @property
    def x(self) -> float:
        return self._wrapped_struct.X

    @x.setter
    def x(self, value: float):
        self._wrapped_struct.X = value

    @property
    def y(self) -> float:
        return self._wrapped_struct.Y

    @y.setter
    def y(self, value: float):
        self._wrapped_struct.Y = value

    @property
    def z(self) -> float:
        return self._wrapped_struct.Z

    @z.setter
    def z(self, value: float):
        self._wrapped_struct.Z = value

    @staticmethod
    def to_rotator(vector: Object.Vector) -> Object.Rotator:
        x, y, z = vector.X, vector.Y, vector.Z
        pitch = math.atan2(z, math.sqrt(x * x + y * y)) * RADIANS_TO_URU
        yaw = math.atan2(y, x) * RADIANS_TO_URU
        return cast(
            "Object.Rotator",
            unrealsdk.make_struct("Rotator", Pitch=int(pitch), Yaw=int(yaw), Roll=0),
        )

    def length(self) -> float:
        return sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self) -> Self:
        length = self.length()
        self.x / length
        self.y / length
        self.z / length
        return self

    def distance(self, other: Vector) -> float:
        return sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2 + (other.z - self.z) ** 2)

    def __add__(self, other: Vector) -> Vector:
        return Vector(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z)

    def __sub__(self, other: Vector) -> Vector:
        return Vector(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z)

    def __mul__(self, other: float) -> Vector:
        return Vector(x=self.x * other, y=self.y * other, z=self.z * other)

    def __truediv__(self, other: float) -> Vector:
        return Vector(x=self.x / other, y=self.y / other, z=self.z / other)


class Rotator:
    """Wrapper around Object.Rotator to provide the math functions."""

    _wrapped_struct: Object.Rotator

    @overload
    def __init__(self, struct: Object.Rotator | Object.Vector | Vector | None = None) -> None: ...
    @overload
    def __init__(self, *, pitch: int = 0, yaw: int = 0, roll: int = 0) -> None: ...
    def __init__(
        self,
        struct: Object.Rotator | Object.Vector | Vector | None = None,
        *,
        pitch: int = 0,
        yaw: int = 0,
        roll: int = 0,
    ) -> None:
        """Initialise a Rotator.

        Can be initialized from either an Object.Rotator, Object.Vector, uemath.Vector,
        or individual pitch, yaw, roll values.
        """
        if struct is not None:
            if isinstance(struct, Vector):
                self._wrapped_struct = Vector.to_rotator(struct.wrapped_struct)
            elif struct._type == ROTATOR_SCRIPT_STRUCT:
                self._wrapped_struct = cast("Object.Rotator", struct)
            elif struct._type == VECTOR_SCRIPT_STRUCT:
                self._wrapped_struct = Vector.to_rotator(cast("Object.Vector", struct))
            return
        self._wrapped_struct = cast(
            "Object.Rotator", unrealsdk.make_struct("Rotator", Pitch=pitch, Yaw=yaw, Roll=roll)
        )

    @property
    def wrapped_struct(self) -> Object.Rotator:
        return self._wrapped_struct

    @property
    def pitch(self) -> int:
        return self._wrapped_struct.Pitch

    @pitch.setter
    def pitch(self, value: int):
        self._wrapped_struct.Pitch = value

    @property
    def yaw(self) -> int:
        return self._wrapped_struct.Yaw

    @yaw.setter
    def yaw(self, value: int):
        self._wrapped_struct.Yaw = value

    @property
    def roll(self) -> int:
        return self._wrapped_struct.Roll

    @roll.setter
    def roll(self, value: int):
        self._wrapped_struct.Roll = value

    @staticmethod
    def to_vector(rotator: Object.Rotator) -> Object.Vector:
        pitch, yaw = rotator.Pitch, rotator.Yaw

        yaw_conv = yaw * URU_TO_RADIANS
        pitch_conv = pitch * URU_TO_RADIANS
        cos_pitch = math.cos(pitch_conv)
        x = math.cos(yaw_conv) * cos_pitch
        y = math.sin(yaw_conv) * cos_pitch
        z = math.sin(pitch_conv)
        return cast("Object.Vector", unrealsdk.make_struct("Vector", X=x, Y=y, Z=z))
