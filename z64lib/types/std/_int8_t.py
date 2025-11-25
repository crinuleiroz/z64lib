from z64lib.types.base import DataType


class s8(DataType, int):
    """ A signed 8-bit integer. """
    format: str = '>b'
    signed: bool = True
    BITS: int = 8
    MIN: int = -0b10000000
    MAX: int = 0b01111111

    def __new__(cls, value: int) -> int:
        return int.__new__(cls, cls._wrap(value))