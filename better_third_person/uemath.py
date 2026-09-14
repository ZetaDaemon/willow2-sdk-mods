# Thanks to juso's uemath lib for the numbers and maths on this.
# https://github.com/juso40/bl2sdk-mods/blob/main/uemath/umath.py
# I reimplemented stuff to work only with the structs, rather than the old tuples.
from __future__ import annotations

import math
from typing import TYPE_CHECKING

import unrealsdk

if TYPE_CHECKING:
    from bl2.Core import Object

    Vector = Object.Vector
    Rotator = Object.Rotator


URU_180 = 32768
URU_TO_RADIANS = math.pi / URU_180
RADIANS_TO_URU = URU_180 / math.pi


def rotator_to_vector(rotator: Rotator) -> Vector:
    pitch, yaw = rotator.Pitch, rotator.Yaw

    yaw_conv = yaw * URU_TO_RADIANS
    pitch_conv = pitch * URU_TO_RADIANS
    cos_pitch = math.cos(pitch_conv)
    x = math.cos(yaw_conv) * cos_pitch
    y = math.sin(yaw_conv) * cos_pitch
    z = math.sin(pitch_conv)
    return unrealsdk.make_struct("Vector", X=x, Y=y, Z=z)  # ty: ignore[invalid-return-type]


def vector_to_rotator(vector: Vector) -> Rotator:
    x, y, z = vector.X, vector.Y, vector.Z
    pitch = math.atan2(z, math.sqrt(x * x + y * y)) * RADIANS_TO_URU
    yaw = math.atan2(y, x) * RADIANS_TO_URU
    return unrealsdk.make_struct("Rotator", Pitch=int(pitch), Yaw=int(yaw), Roll=0)  # ty: ignore[invalid-return-type]


def multiply_vector_float(a: Vector, b: float) -> Vector:
    return unrealsdk.make_struct("Vector", X=a.X * b, Y=a.Y * b, Z=a.Z * b)  # ty: ignore[invalid-return-type]


def vector_add(a: Vector, b: Vector) -> Vector:
    return unrealsdk.make_struct("Vector", X=a.X + b.X, Y=a.Y + b.Y, Z=a.Z + b.Z)  # ty: ignore[invalid-return-type]


def vector_sub(a: Vector, b: Vector) -> Vector:
    return unrealsdk.make_struct("Vector", X=a.X - b.X, Y=a.Y - b.Y, Z=a.Z - b.Z)  # ty: ignore[invalid-return-type]
