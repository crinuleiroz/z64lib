"""
z64lib.types
=====

A ctypes-like system for defining and parsing Zelda64 binary structs.
"""
from .base import DataType
from .markers import *
from .primitives import *
from .references import pointer
from .composites import *


__all__ = [
    # Base
    "DataType",
    # Type Markers
    "PointerType",
    "ArrayType",
    "BitfieldType",
    "UnionType",
    "StructType",
    # Primitives
    "s8",
    "u8",
    "s16",
    "u16",
    "s32",
    "u32",
    "s64",
    "u64",
    "f32",
    # Non-standard Primitives
    "s24",
    "u24",
    # References
    "pointer",
    # Composites
    "array",
    "bitfield",
    "union",
    "Z64Struct",
    "DynaStruct",
]