import struct
from z64lib.types import DataType


class pointer(DataType):
    """ An unsigned 32-bit integer that indicates an offset to a new structure in the binary data. """
    _LEVEL_MAP = {
        "single": 1,
        "double": 2,
    }

    def __init__(self, struct_type, pointer_type: str | int = "single"):
        self.struct_type = struct_type

        if isinstance(pointer_type, str):
            if pointer_type.lower() not in self._LEVEL_MAP:
                raise ValueError()
            self.pointer_type = self._LEVEL_MAP[pointer_type.lower()]
        elif isinstance(pointer_type, int):
            self.pointer_type = pointer_type
        else:
            raise TypeError("pointer_type must be str or int.")

    def from_bytes(self, buffer: bytes, offset: int):
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
            if self.pointer_type == 1:
                self._resolve_pointer(buffer, addr)
            else:
                self._resolve_pointer_to_pointer(buffer, addr)
        except Exception as e:
            print(f"warning: failed to parse {self.struct_type.__name__} at 0x{addr:X}: {e}")
            return None

    def to_bytes(self, value):
        if not value:
            return struct.pack('>I', 0)

        addr = getattr(value, '_address', None)
        if addr is None:
            addr = getattr(value, '_original_address', 0)

        return struct.pack('>I', addr)

    def _resolve_pointer(self, buffer, addr):
        obj = self.struct_type.from_bytes(buffer, addr)
        obj._original_address = addr # Store the original address just in case
        return obj

    def _resolve_pointer_to_pointer(self, buffer, addr):
        next_pointer = pointer(self.struct_type, self.pointer_type - 1)
        return next_pointer.from_bytes(buffer, addr)

    @classmethod
    def size(cls):
        return 4