from z64lib.types.base import DataType
from z64lib.types.markers import PrimitiveType


class s32(DataType, PrimitiveType, int):
    """ A signed 32-bit integer. """
    format: str = '>i'
    signed: bool = True
    BITS: int = 32
    MIN: int = -0b10000000000000000000000000000000
    MAX: int = 0b01111111111111111111111111111111

    def __new__(cls, value: int) -> int:
        return int.__new__(cls, cls._wrap(value))