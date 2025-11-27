from z64lib.types.base import DataType
from z64lib.types.markers import ArrayType


class array(DataType, ArrayType):
    """ Represents a fixed-size array of field types. """
    data_type: type = None
    length: int = 0

    def __class_getitem__(cls, params):
        """"""
        if not isinstance(params, tuple):
            data_type = params
            length = None
        else:
            if len(params) != 2:
                raise TypeError('array[...] must be array[T] or array[T, length]')
            data_type, length = params
            if length is not None and (not isinstance(length, int) or length < 0):
                raise TypeError('length must be a positive integer')

        return type(
            f'array_{data_type.__name__}_{length}',
            (cls,),
            {
                'data_type': data_type,
                'length': length,
            },
        )

    def __init__(self, items=None):
        self.items = items if items is not None else []

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, i):
        return self.items[i]

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return repr(self.items)

    def __str__(self):
        return str(self.items)

    @property
    def signed(self):
        return getattr(self.data_type, 'signed', False)

    @classmethod
    def size(cls):
        if cls.length is None:
            raise TypeError('Dynamic array has no static size.')
        return cls.data_type.size() * cls.length

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int, length: int | None = None):
        """"""
        if cls.length is None:
            if length is None:
                raise TypeError('Dynamic array requires a length argument.')
            actual_len = length
        else:
            actual_len = cls.length

        items = []
        size = cls.data_type.size()

        for i in range(actual_len):
            item_offset = offset + i * size
            item = cls.data_type.from_bytes(buffer, item_offset)
            items.append(item)

        return cls(items)

    def to_bytes(self):
        data = bytearray()
        for v in self.items:
            data += self.data_type.to_bytes(v)
        return bytes(data)