from .primitives import *
from .composites import *
from .references import *


#region Standard
# 8-bit
int8_t = int8 = z64_byte = s8
uint8_t = uint8 = z64_ubyte = u8

# 16-bit
int16_t = int16 = z64_short = s16
uint16_t = uint16 = z64_ushort = u16

# 32-bit
int32_t = int32 = z64_int = s32
uint32_t = uint32 = z64_uint = u32

# 64-bit
int64_t = int64 = z64_longlong = s64
uint64_t = uint64 = z64_ulonglong = u64

# Floating-point
float32 = z64_float = f32
float64 = z64_double = f64

# Bitfield
z64_bitfield = zbitfield = bitfield

# Union
z64_union = zunion = union

# Array
z64_array = zarray = array

# Struct
z64_struct = zstruct = Z64Struct
dyna_struct = dstruct = DynaStruct

# Pointer
z64_pointer = zpointer = pointer
#endregion

#region Non-standard
int24_t = int24 = s24
uint24_t = uint24 = u24
#endregion


__all__ = [
    # 8-bit
    'int8_t',
    'int8',
    'z64_byte',
    'uint8_t',
    'uint8',
    'z64_ubyte',
    # 16-bit
    'int16_t',
    'int16',
    'z64_short',
    'uint16_t',
    'uint16',
    'z64_ushort',
    # 32-bit
    'int32_t',
    'int32',
    'z64_int',
    'uint32_t',
    'uint32',
    'z64_uint',
    # 64-bit
    'int64_t',
    'int64',
    'z64_longlong',
    'uint64_t',
    'uint64',
    'z64_ulonglong',
    # Floating-point
    'float32',
    'z64_float',
    'float64',
    'z64_double',
    # Bitfield
    'z64_bitfield',
    'zbitfield',
    'bitfield',
    # Union
    'z64_union',
    'zunion',
    'union',
    # Array
    'z64_array',
    'zarray',
    'array',
    # Struct
    'z64_struct',
    'zstruct',
    'dyna_struct',
    'dstruct',
    # Pointer
    'z64_pointer',
    'zpointer',
    'pointer',
    # Non-standard
    'int24_t',
    'int24',
    'uint24_t',
    'uint24',
]