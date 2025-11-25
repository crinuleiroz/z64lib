from z64lib.types.base import DataType
from z64lib.types.markers import PrimitiveType


class u8(DataType, PrimitiveType, int):
    """ An unsigned 8-bit integer. """
    format: str = '>B'
    signed: bool = False
    BITS: int = 8
    MIN: int = 0b00000000
    MAX: int = 0b11111111

    def __new__(cls, value: int) -> int:
        return int.__new__(cls, cls._wrap(value))