from z64lib.types.base import DataType
from z64lib.types.markers import PrimitiveType


class s8(DataType, PrimitiveType, int):
    """ A signed 8-bit integer. """
    format: str = '>b'
    signed: bool = True

    # Bit Width and Min/Max
    BITS: int = 8
    MIN: int = -0b10000000
    MAX: int = 0b01111111

    # Type Flags
    is_primitive: bool = True

    def __new__(cls, value: int) -> int:
        return int.__new__(cls, cls._wrap(value))