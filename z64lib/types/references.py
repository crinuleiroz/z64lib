import struct
from z64lib.types import DataType


class pointer(DataType):
    """ An unsigned 32-bit integer that indicates an offset to a new structure in the binary data. """
    def __init__(self, struct_type):
        self.struct_type = struct_type

    def from_bytes(self, buffer: bytes, offset: int) -> object:
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

        # Begin instantiation of the object. After the object is instantiated,
        # store the pointer's raw bytes value in the class for binary serialization.
        try:
            obj = self.struct_type.from_bytes(buffer, addr)
            obj._original_address = addr # Store the original address just in case
            return obj
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

    @classmethod
    def size(cls):
        return 4