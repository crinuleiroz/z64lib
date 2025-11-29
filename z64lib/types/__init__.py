"""
z64lib.types
=====

A ctypes-like system for defining and parsing Zelda64 binary structs.
"""
from .base import *
from .markers import *
from .primitives import *
from .references import *
from .composites import *


__all__ = [
    # Base
    'DataType',
    'Field',
    'primitive_from_bytes',
    'bitfield_from_bytes',
    'composite_from_bytes',
    'pointer_from_bytes',
    'primitive_to_bytes',
    'bitfield_to_bytes',
    'composite_to_bytes',
    'pointer_to_bytes',
    'FROM_BYTES_HANDLERS',
    'TO_BYTES_HANDLERS',
    # Type Markers
    'PointerType',
    'ArrayType',
    'BitfieldType',
    'UnionType',
    'StructType',
    # Primitives
    's8',
    'u8',
    's16',
    'u16',
    's32',
    'u32',
    's64',
    'u64',
    'f32',
    'f64',
    # Non-standard Primitives
    's24',
    'u24',
    # References
    'pointer',
    # Composites
    'array',
    'bitfield',
    'union',
    'Z64Struct',
    'DynaStruct',
]