from z64lib.types.base import DataType


class f32(DataType, float):
    """ A 32-bit single-precision floating-point value. """
    format: str = '>f'
    signed: bool = True
    BITS: int = 32
    MIN: float = -3.4028235e38
    MAX: float = 3.4028235e38

    def __new__(cls, value: float) -> float:
        return float.__new__(cls, value)