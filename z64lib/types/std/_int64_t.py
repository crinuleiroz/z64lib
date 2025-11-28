from z64lib.types.base import DataType
from z64lib.types.markers import PrimitiveType


class s64(DataType, PrimitiveType, int):
    """ A signed 64-bit integer. """
    format: str = '>q'
    signed: bool = True

    # Bit Width and Min/Max
    BITS: int = 64
    MIN: int = -0b1000000000000000000000000000000000000000000000000000000000000000
    MAX: int = 0b0111111111111111111111111111111111111111111111111111111111111111

    # Type Flags
    is_primitive: bool = True

    def __new__(cls, value: int) -> int:
        return int.__new__(cls, cls._wrap(value))