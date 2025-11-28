from z64lib.types.base import DataType
from z64lib.types.markers import PointerType


class pointer(DataType, PointerType):
    """ An unsigned 32-bit integer that indicates an offset to a new structure in the binary data. """
    format: str = '>I'
    signed: bool = False

    # Bit Width and Min/Max
    BITS: int = 32
    MIN: int = 0b00000000000000000000000000000000
    MAX: int = 0b11111111111111111111111111111111

    # Type Flags
    is_pointer: bool = True

    # Pointer specific data
    _DEPTH_MAP: dict[str, int] = {
        'single': 1,
        'double': 2,
    }
    data_type: DataType = None
    pointer_depth: int = 1

    def __class_getitem__(cls, params):
        """"""
        if not isinstance(params, tuple):
            data_type, depth = params, 1
        else:
            if len(params) != 2:
                raise TypeError("Pointer type must be pointer[T] or pointer[T, depth]")
            data_type, depth = params

        if isinstance(depth, str):
            if depth not in cls._DEPTH_MAP:
                raise ValueError(f"Unknown pointer depth: {depth}")
            depth = cls._DEPTH_MAP[depth]

        if not isinstance(depth, int) or depth < 1:
            raise TypeError("Pointer depth must be a positive integer")

        return type(
            f'pointer_to_{data_type.__name__}_d{depth}',
            (cls,),
            {
                'data_type': data_type,
                'pointer_depth': depth,
            },
        )

    def __init__(self, reference: DataType = None, target_address: int = 0,
                 original_address: int = 0, nullable: bool = True):
        self.reference = reference
        self.target_address = target_address
        self.original_address = original_address
        self.allocated_address = 0 # Consistency only, never used
        self.nullable = nullable

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        """"""
        target_address = cls._get_struct().unpack_from(buffer, offset)[0]
        return cls(None, target_address, offset)

    def dereference(self, buffer: bytes, resolve_all: bool = False):
        """"""
        if self.target_address == 0 or self.target_address >= len(buffer):
            self.reference = None
            if not self.nullable:
                raise ValueError(f"Pointer at offset {self.original_address} cannot be null")
            return None

        if self.pointer_depth == 1:
            self.reference = self.data_type.from_bytes(buffer, self.target_address)
            self.reference.original_address = self.target_address
        else:
            next_ptr_cls = pointer[self.data_type, self.pointer_depth - 1]
            self.reference = next_ptr_cls().from_bytes(buffer, self.target_address)

        if resolve_all:
            current = self.reference
            while isinstance(current, pointer):
                current = current.dereference(buffer, resolve_all=True)
            self.reference = current

        return self.reference

    def to_bytes(self):
        """"""
        addr = self.address
        if addr is None:
            raise ValueError(f"Pointer {self} cannot be null")
        return self._get_struct().pack(self.address)

    @property
    def address(self):
        if self.reference is None:
            return 0 if self.nullable else None
        return getattr(self.reference, 'allocated_address', 0) or getattr(self.reference, 'original_address', 0)

__all__ = [
    'pointer',
]