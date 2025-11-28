import struct
from z64lib.types.base import DataType
from z64lib.types.markers import PointerType


class pointer(DataType, PointerType):
    """ An unsigned 32-bit integer that indicates an offset to a new structure in the binary data. """
    _DEPTH_MAP = {
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

    def __init__(self, addr=None, obj=None):
        self.addr = addr
        self.obj = obj

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        """
        Instantiates a structure referenced by this pointer from binary data.

        Parameters
        ----------
        buffer: bytes
            Binary struct data.
        offset: int
            Offset to the struct.

        Returns
        ----------
        object
            Returns a fully instantiated object for the given struct type.
            If the address is 0 or out of bounds, returns None instead.
        """
        addr = struct.unpack_from('>I', buffer, offset)[0]
        return cls(addr=addr)

    def dereference(self, buffer: bytes):
        if self.addr == 0 or self.addr >= len(buffer):
            self.obj = None
        elif self.pointer_depth == 1:
            self.obj = self.data_type.from_bytes(buffer, self.addr)
            self.obj._original_address = self.addr
        else:
            self.obj = pointer[self.data_type, self.pointer_depth - 1](addr=self.addr).deref(buffer)
        return self.obj

    def to_bytes(self):
        addr = getattr(self.obj, '_address', self.addr or 0)
        return struct.pack('>I', addr)

    @classmethod
    def size(cls):
        return 4


__all__ = [
    'pointer',
]