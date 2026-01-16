"""
### z64lib.ultratypes.aliases
"""
from .primitives import *
from .composites import *
from .references import *


#region Standard
# 8-bit
z64_signed_char = z64_int8 = int8 = s8
z64_unsigned_char = z64_uint8 = uint8 = u8

# 16-bit
z64_signed_short = z64_int16 = int16 = s16
z64_unsigned_short = z64_uint16 = uint16 = u16

# 32-bit
z64_signed_long = z64_int32 = int32 = s32
z64_unsigned_long = z64_uint32 = uint32 = u32

# 64-bit
z64_signed_long_long = z64_int64 = int64 = s64
z64_unsigned_long_long = z64_uint64 = uint64 = u64

# Floating-point
z64_float = z64_float32 = float32 = f32
z64_double = z64_float64 = float64 = f64

# Bitfield
z64_bitfield = bitfield

# Union
z64_union = union

# Array
z64_array = array

# Struct
z64_struct = structure

# Pointer
z64_pointer = pointer
#endregion

#region Non-standard
z64_int24 = int24 = s24
z64_uint24 = uint24 = u24
#endregion


#region Star Imports
__all__ = [
    # 8-bit
    'z64_signed_char', 'z64_int8', 'int8', 'z64_unsigned_char', 'z64_uint8', 'uint8',
    # 16-bit
    'z64_signed_short', 'z64_int16', 'int16', 'z64_unsigned_short', 'z64_uint16', 'uint16',
    # 32-bit
    'z64_signed_long', 'z64_int32', 'int32', 'z64_unsigned_long', 'z64_uint32', 'uint32',
    # 64-bit
    'z64_signed_long_long', 'z64_int64', 'int64', 'z64_unsigned_long_long', 'z64_uint64', 'uint64',
    # Floating-point
    'z64_float', 'z64_float32', 'float32', 'z64_double', 'z64_float64', 'float64',
    # Bitfield
    'z64_bitfield',
    # Union
    'z64_union',
    # Array
    'z64_array',
    # Struct
    'z64_struct',
    # Pointer
    'z64_pointer',
    # Non-standard
    'z64_int24', 'int24', 'z64_uint24', 'uint24',
]
#endregion