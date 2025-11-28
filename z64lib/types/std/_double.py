from z64lib.types.base import DataType
from z64lib.types.markers import PrimitiveType


class f64(DataType, PrimitiveType, float):
    """ A 64-bit double-precision floating-point value. """
    format: str = '>d'
    signed: bool = True

    # Bit Width and Min/Max
    BITS: int = 64
    MIN: float = -1.7976931348623157e308
    MAX: float = 1.7976931348623157e308

    # Type Flags
    is_primitive: bool = True

    def __new__(cls, value: float) -> float:
        return float.__new__(cls, value)