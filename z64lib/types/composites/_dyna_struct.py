from ._z64_struct import Z64Struct
from z64lib.types.markers import *


class DynaStruct(Z64Struct):
    """
    Base class for dynamically sized Zelda64 structs.
    Automatically computes size based on content.
    """
    def size(self) -> int:
        obj = self

        def callback(name, data_type, offset):
            value = getattr(obj, name, None)

            # Nested structs
            if isinstance(value, Z64Struct):
                return offset + value.size()

            # Bitfield
            if issubclass(data_type, BitfieldType):
                return offset + data_type.size()

            # Primitives, pointers, and arrays
            if issubclass(data_type, ArrayType):
                if value is not None:
                    return offset + len(value) * data_type.data_type.size()
                return offset + (data_type.size() if data_type.length is not None else 0)

            return offset + data_type.size()

        offset = self.walk_fields(self._fields_, callback)
        return self.align_to(offset, getattr(self, '_align_', 1))