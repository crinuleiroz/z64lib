from z64lib.types.base import DataType


class u24(DataType, int):
    """ An unsigned 24-bit integer. """
    format: str = None
    signed: bool = False
    BITS: int = 24
    MIN: int = 0b000000000000000000000000
    MAX: int = 0b111111111111111111111111

    def __new__(cls, value: int) -> int:
        return int.__new__(cls, cls._wrap(value))