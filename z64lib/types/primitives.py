from z64lib.types import DataType


class u8(DataType, int):
    """ An unsigned 8-bit integer. """
    format: str = '>B'
    signed: bool = False
    BITS: int = 8
    MIN: int = 0b00000000
    MAX: int = 0b11111111

    def __new__(cls, value: int) -> int:
        return int.__new__(cls, cls._wrap(value))


class s8(DataType, int):
    """ A signed 8-bit integer. """
    format: str = '>b'
    signed: bool = True
    BITS: int = 8
    MIN: int = -0b10000000
    MAX: int = 0b01111111

    def __new__(cls, value: int) -> int:
        return int.__new__(cls, cls._wrap(value))


class u16(DataType, int):
    """ An unsigned 16-bit integer. """
    format: str = '>H'
    signed: bool = False
    BITS: int = 16
    MIN: int = 0b0000000000000000
    MAX: int = 0b1111111111111111

    def __new__(cls, value: int) -> int:
        return int.__new__(cls, cls._wrap(value))


class s16(DataType, int):
    """ A signed 16-bit integer. """
    format: str = '>h'
    signed: bool = True
    BITS: int = 16
    MIN: int = -0b1000000000000000
    MAX: int = 0b0111111111111111

    def __new__(cls, value: int) -> int:
        return int.__new__(cls, cls._wrap(value))


class u32(DataType, int):
    """ An unsigned 32-bit integer. """
    format: str = '>I'
    signed: bool = False
    BITS: int = 32
    MIN: int = 0b00000000000000000000000000000000
    MAX: int = 0b11111111111111111111111111111111

    def __new__(cls, value: int) -> int:
        return int.__new__(cls, cls._wrap(value))


class s32(DataType, int):
    """ A signed 32-bit integer. """
    format: str = '>i'
    signed: bool = True
    BITS: int = 32
    MIN: int = -0b10000000000000000000000000000000
    MAX: int = 0b01111111111111111111111111111111

    def __new__(cls, value: int) -> int:
        return int.__new__(cls, cls._wrap(value))


class u64(DataType, int):
    """ An unsigned 64-bit integer. """
    format: str = '>Q'
    signed: bool = False
    BITS: int = 64
    MIN: int = 0b0000000000000000000000000000000000000000000000000000000000000000
    MAX: int = 0b1111111111111111111111111111111111111111111111111111111111111111

    def __new__(cls, value: int) -> int:
        return int.__new__(cls, cls._wrap(value))


class s64(DataType, int):
    """ A signed 64-bit integer. """
    format: str = '>q'
    signed: bool = True
    BITS: int = 64
    MIN: int = -0b1000000000000000000000000000000000000000000000000000000000000000
    MAX: int = 0b0111111111111111111111111111111111111111111111111111111111111111

    def __new__(cls, value: int) -> int:
        return int.__new__(cls, cls._wrap(value))


class f32(DataType, float):
    """ A 32-bit single-precision floating-point value. """
    format: str = '>f'
    signed: bool = True
    BITS: int = 32
    MIN: float = -3.4028235e38
    MAX: float = 3.4028235e38

    def __new__(cls, value: float) -> float:
        return float.__new__(cls, value)
