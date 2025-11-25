from z64lib.types.base import DataType


class s64(DataType, int):
    """ A signed 64-bit integer. """
    format: str = '>q'
    signed: bool = True
    BITS: int = 64
    MIN: int = -0b1000000000000000000000000000000000000000000000000000000000000000
    MAX: int = 0b0111111111111111111111111111111111111111111111111111111111111111

    def __new__(cls, value: int) -> int:
        return int.__new__(cls, cls._wrap(value))