from ._z64_struct import Z64Struct
from z64lib.types.markers import *
from z64lib.types.composites import array
from z64lib.types._internals import walk_fields

class DynaStruct(Z64Struct):
    """
    Base class for dynamically sized Zelda64 structs.
    Automatically computes size based on content.
    """
    def size(self) -> int:
        obj = self

        def callback(name, data_type, offset, extra):
            value = getattr(obj, name, None)

            # Nested structs
            if isinstance(value, Z64Struct):
                return offset + value.size()

            # Grouped bitfields
            if extra:
                base_type = extra[0][1]
                return offset + base_type.size()

            # Primitives, pointers, and arrays
            if isinstance(data_type, array):
                if value is not None:
                    return offset + len(value) * data_type.data_type.size()
                return offset + data_type.size()

            return offset + data_type.size()

        offset = walk_fields(self._fields_, callback)
        return self.align_to(offset, getattr(self, '_align_', 1))