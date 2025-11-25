from z64lib.types.base import DataType


class u16(DataType, int):
    """ An unsigned 16-bit integer. """
    format: str = '>H'
    signed: bool = False
    BITS: int = 16
    MIN: int = 0b0000000000000000
    MAX: int = 0b1111111111111111

    def __new__(cls, value: int) -> int:
        return int.__new__(cls, cls._wrap(value))