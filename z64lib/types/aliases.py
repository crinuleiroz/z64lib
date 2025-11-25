from .primitives import *
from .composites import *


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

# Float
float32 = z64_float = f32

# Struct
z64_struct = Z64Struct
dyna_struct = DynaStruct
#endregion


#region Non-standard
int24_t = int24 = s24
uint24_t = uint24 = u24
#endregion


__all__ = [
    "int8_t",
    "int8",
    "z64_byte",
    "uint8_t",
    "uint8",
    "z64_ubyte",
    "int16_t",
    "int16",
    "z64_short",
    "uint16_t",
    "uint16",
    "z64_ushort",
    "int32_t",
    "int32",
    "z64_int",
    "uint32_t",
    "uint32",
    "z64_uint",
    "int64_t",
    "int64",
    "z64_longlong",
    "uint64_t",
    "uint64",
    "z64_ulonglong",
    "float32",
    "z64_float",
    "z64_struct",
    "dyna_struct",
    "int24_t",
    "int24",
    "uint24_t",
    "uint24",
]