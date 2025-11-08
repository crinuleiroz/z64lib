import struct
from z64lib.types import DataType


class u8(DataType):
    """ An unsigned 8-bit integer. """
    signed: bool = False

    @classmethod
    def size(cls):
        return 1

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        return struct.unpack_from('>B', buffer, offset)[0]

    @classmethod
    def to_bytes(cls, value):
        return struct.pack('>B', value)



class s8(DataType):
    """ A signed 8-bit integer. """
    signed: bool = True

    @classmethod
    def size(cls):
        return 1

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        return struct.unpack_from('>b', buffer, offset)[0]

    @classmethod
    def to_bytes(cls, value):
        return struct.pack('>b', value)



class u16(DataType):
    """ An unsigned 16-bit integer. """
    signed: bool = False

    @classmethod
    def size(cls):
        return 2

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        return struct.unpack_from('>H', buffer, offset)[0]

    @classmethod
    def to_bytes(cls, value):
        return struct.pack('>H', value)



class s16(DataType):
    """ A signed 16-bit integer. """
    signed: bool = True

    @classmethod
    def size(cls):
        return 2

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        return struct.unpack_from('>h', buffer, offset)[0]

    @classmethod
    def to_bytes(cls, value):
        return struct.pack('>h', value)



class u32(DataType):
    """ An unsigned 32-bit integer. """
    signed: bool = False

    @classmethod
    def size(cls):
        return 4

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        return struct.unpack_from('>I', buffer, offset)[0]

    @classmethod
    def to_bytes(cls, value):
        return struct.pack('>I', value)



class s32(DataType):
    """ A signed 32-bit integer. """
    signed: bool = True

    @classmethod
    def size(cls):
        return 4

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        return struct.unpack_from('>i', buffer, offset)[0]

    @classmethod
    def to_bytes(cls, value):
        return struct.pack('>i', value)



class f32(DataType):
    """ A 32-bit single-precision floating-point value. """
    signed: bool = True

    @classmethod
    def size(cls):
        return 4

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        return struct.unpack_from('>f', buffer, offset)[0]

    @classmethod
    def to_bytes(cls, value):
        return struct.pack('>f', value)
