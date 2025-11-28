from z64lib.types.base import DataType
from z64lib.types.markers import PrimitiveType


class s24(DataType, PrimitiveType, int):
    """ A signed 24-bit integer. """
    format: str = None
    signed: bool = True

    # Bit Width and Min/Max
    BITS: int = 24
    MIN: int = -0b100000000000000000000000
    MAX: int = 0b011111111111111111111111

    # Type Flags
    is_primitive: bool = True

    def __new__(cls, value: int) -> int:
        return int.__new__(cls, cls._wrap(value))