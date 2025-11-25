from ._accessors import UnionAccessor
import inspect
from z64lib.types.base import DataType
from z64lib.types.markers import *


class union(DataType, UnionType):
    """ A struct member whose memory is shared by multiple values. """
    def __init__(self, *fields):
        self._fields = fields

    def size(self):
        sizes = []

        for name, data_type in self._fields:
            sizes.append(data_type.size())

        return max(sizes)

    def from_bytes(self, buffer: bytes | bytearray, offset: int):
        values = {}

        for name, data_type in self._fields:
            if inspect.isclass(data_type) and issubclass(data_type, StructType):
                values[name] = data_type.from_bytes(buffer, offset)
            else:
                values[name] = data_type.from_bytes(buffer, offset)

        return UnionAccessor(values)

    def to_bytes(self, accessor: UnionAccessor) -> bytes:
        active_name = accessor.active_field
        if active_name not in accessor._values:
            raise ValueError()

        value = accessor._values[active_name]
        data_type = None
        for name, f_type in self._fields:
            if name == active_name:
                data_type = f_type
                break

        if data_type is None:
            raise ValueError()

        if inspect.isclass(data_type) and issubclass(data_type, StructType):
            return value.to_bytes()
        else:
            return data_type.to_bytes(value)