"""
### z64lib.ultratypes
"""
from .base import *
from .primitives import *
from .composites import *
from .references import *


__all__ = [
    # Base
    'TypeFlag', 'DataType',
    # Primitives
    'primitive', 's8', 'u8', 's16', 'u16', 's32', 'u32', 's64', 'u64', 'f32', 'f64', 's24', 'u24',
    # Composites
    'bitfield', 'union', 'array', 'structure',
    # References
    'pointer',
]