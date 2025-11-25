from z64lib.types.base import DataType


class u32(DataType, int):
    """ An unsigned 32-bit integer. """
    format: str = '>I'
    signed: bool = False
    BITS: int = 32
    MIN: int = 0b00000000000000000000000000000000
    MAX: int = 0b11111111111111111111111111111111

    def __new__(cls, value: int) -> int:
        return int.__new__(cls, cls._wrap(value))