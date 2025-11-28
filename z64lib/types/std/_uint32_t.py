from z64lib.types.base import DataType
from z64lib.types.markers import PrimitiveType


class u32(DataType, PrimitiveType, int):
    """ An unsigned 32-bit integer. """
    format: str = '>I'
    signed: bool = False

    # Bit Width and Min/Max
    BITS: int = 32
    MIN: int = 0b00000000000000000000000000000000
    MAX: int = 0b11111111111111111111111111111111

    # Type Flags
    is_primitive: bool = True

    def __new__(cls, value: int) -> int:
        return int.__new__(cls, cls._wrap(value))