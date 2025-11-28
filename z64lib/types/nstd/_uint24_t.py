from z64lib.types.base import DataType
from z64lib.types.markers import PrimitiveType


class u24(DataType, PrimitiveType, int):
    """ An unsigned 24-bit integer. """
    format: str = None
    signed: bool = False

    # Bit Width and Min/Max
    BITS: int = 24
    MIN: int = 0b000000000000000000000000
    MAX: int = 0b111111111111111111111111

    # Type Flags
    is_primitive: bool = True

    def __new__(cls, value: int) -> int:
        return int.__new__(cls, cls._wrap(value))