from z64lib.types.base import DataType
from z64lib.types.markers import PrimitiveType


class u64(DataType, PrimitiveType, int):
    """ An unsigned 64-bit integer. """
    format: str = '>Q'
    signed: bool = False
    BITS: int = 64
    MIN: int = 0b0000000000000000000000000000000000000000000000000000000000000000
    MAX: int = 0b1111111111111111111111111111111111111111111111111111111111111111

    def __new__(cls, value: int) -> int:
        return int.__new__(cls, cls._wrap(value))