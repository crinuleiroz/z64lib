"""
z64lib.types
=====

A ctypes-like system for defining and parsing Zelda64 binary structs.
"""
from .base import DataType
from .primitives import (
    u8, s8, u16, s16, u32, s32, u64, s64, f32
)
from .references import (
    pointer
)
from .composites import (
    array, bitfield, union, Z64Struct, DynaStruct
)


__all__ = [
    # Base
    "DataType",
    # Primitives
    "u8",
    "s8",
    "u16",
    "s16",
    "u32",
    "s32",
    "u64",
    "s64",
    "f32",
    # References
    "pointer",
    # Composites
    "array",
    "bitfield",
    "union",
    "Z64Struct",
    "DynaStruct"
]