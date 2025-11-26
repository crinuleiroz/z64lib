import struct
from z64lib.types.base import DataType
from z64lib.types.markers import PointerType


class pointer(DataType, PointerType):
    """ An unsigned 32-bit integer that indicates an offset to a new structure in the binary data. """
    _DEPTH_MAP = {
        "single": 1,
        "double": 2,
    }

    struct_type: type = None
    pointer_depth: int = 1

    def __class_getitem__(cls, params):
        """"""
        if not isinstance(params, tuple):
            struct_type, depth = params, 1
        else:
            if len(params) != 2:
                raise TypeError("pointer[...] must be pointer[T] or pointer[T, depth].")
            struct_type, depth = params

        if not isinstance(depth, int) or depth < 1:
            raise TypeError("pointer depth must be a positive integer.")

        return type(
            f'pointer_to_{struct_type.__name__}_d{depth}',
            (cls,),
            {
                'struct_type': struct_type,
                'pointer_depth': depth,
            },
        )

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
        try:
            addr = struct.unpack_from('>I', buffer, offset)[0]
        except struct.error:
            return None

        if addr == 0 or addr >= len(buffer):
            return None

        # Begin resolving pointer to instantiate an object. If the pointer points to
        # another pointer, then go another level deeper to find the source data.
        try:
            return cls._resolve(buffer, addr, cls.pointer_depth)
        except Exception as e:
            print(f"warning: failed to parse {cls.struct_type.__name__} at 0x{addr:X}: {e}")
            return None

    @classmethod
    def _resolve(cls, buffer, addr, depth):
        if depth == 1:
            obj = cls.struct_type.from_bytes(buffer, addr)
            obj._original_address = addr
            return obj

        next_ptr_type = pointer[cls.struct_type, depth - 1]
        return next_ptr_type.from_bytes(buffer, addr)

    @classmethod
    def to_bytes(self, value):
        if not value:
            return struct.pack('>I', 0)

        addr = getattr(value, '_address', None)
        if addr is None:
            addr = getattr(value, '_original_address', 0)

        return struct.pack('>I', addr)

    @classmethod
    def size(cls):
        return 4


__all__ = [
    "pointer",
]