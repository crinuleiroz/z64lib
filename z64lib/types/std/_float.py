from z64lib.types.base import DataType
from z64lib.types.markers import PrimitiveType


class f32(DataType, PrimitiveType, float):
    """ A 32-bit single-precision floating-point value. """
    format: str = '>f'
    signed: bool = True
    BITS: int = 32
    MIN: float = -3.4028235e38
    MAX: float = 3.4028235e38

    def __new__(cls, value: float) -> float:
        return float.__new__(cls, value)