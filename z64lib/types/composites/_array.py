from z64lib.types.base import DataType
from z64lib.types.markers import ArrayType

class array(DataType, ArrayType):
    """ Represents a fixed-size array of field types. """
    def __init__(self, data_type: DataType, length: int):
        self.data_type = data_type
        self.length = length
        self.items = []

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, index):
        return self.items[index]

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return repr(self.items)

    def __str__(self):
        return str(self.items)

    @property
    def signed(self):
        return getattr(self.data_type, 'signed', False)

    def size(self):
        return self.data_type.size() * self.length

    def from_bytes(self, buffer: bytes, offset: int):
        self.items = []

        for i in range(self.length):
            item_offset = offset + i * self.data_type.size()
            item = self.data_type.from_bytes(buffer, item_offset)
            self.items.append(item)

        return self

    def to_bytes(self, values):
        data = bytearray()

        for v in values:
            data += self.data_type.to_bytes(v)

        return bytes(data)