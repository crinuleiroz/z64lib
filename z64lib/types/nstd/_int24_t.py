from z64lib.types.base import DataType


class s24(DataType, int):
    """ A signed 24-bit integer. """
    format: str = None
    signed: bool = True
    BITS: int = 24
    MIN: int = -0b100000000000000000000000
    MAX: int = 0b011111111111111111111111

    def __new__(cls, value: int) -> int:
        return int.__new__(cls, cls._wrap(value))