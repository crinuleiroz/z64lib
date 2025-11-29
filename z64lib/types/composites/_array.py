from z64lib.types.base import DataType, FROM_BYTES_HANDLERS
from z64lib.types.markers import ArrayType


class array(DataType, ArrayType):
    """ Represents a fixed-size array of field types. """
    # Type Flags
    is_array: bool = True

    # Static/Dynamic Flags
    is_static: bool = True
    is_dyna: bool = False

    # Array specific data
    data_type: type = None
    length: int = 0

    def __class_getitem__(cls, params):
        if not isinstance(params, tuple):
            data_type = params
            length = None
        else:
            if len(params) != 2:
                raise TypeError("Array type must be array[T] or array[T, length]")
            data_type, length = params
            if length is not None and (not isinstance(length, int) or length < 0):
                raise TypeError("Array length must be a positive integer")

        # Determine static vs. dynamic
        is_static = length not in (None, 0)
        is_dyna = length in (None, 0)

        return type(
            f'array_{data_type.__name__}_{length}',
            (cls,),
            {
                'data_type': data_type,
                'length': length,
                'is_static': is_static,
                'is_dyna': is_dyna,
            },
        )

    def __init__(self, items=[], original_address: int = 0, allocated_address: int = 0):
        self.items = []

        for item in items:
            if isinstance(item, self.data_type):
                self.items.append(item)
            elif getattr(self.data_type, 'is_primitive', False):
                self.items.append(self.data_type(item))
            elif getattr(self.data_type, 'is_array', False):
                if isinstance(item, self.data_type):
                    self.items.append(item)
                else:
                    raise TypeError(f"Cannot initialize nested array from {item}")
            elif getattr(self.data_type, 'is_struct', False):
                if isinstance(item, self.data_type):
                    self.items.append(item)
                else:
                    raise TypeError(f"Cannot initialize struct array from {item}")
            elif getattr(self.data_type, 'is_pointer', False):
                if isinstance(item, self.data_type):
                    self.items.append(item)
                else:
                    raise TypeError(f"Cannot initialize pointer array from {item}")
            elif getattr(self.data_type, 'is_bitfield', False):
                if isinstance(item, self.data_type):
                    self.items.append(item)
                else:
                    raise TypeError(f"Cannot initialize bitfield array from {item}")
            elif getattr(self.data_type, 'is_union', False):
                if isinstance(item, self.data_type):
                    self.items.append(item)
                else:
                    raise TypeError(f"Cannot initialize union array from {item}")
            else:
                raise TypeError(f"Cannot wrap {item} in {self.data_type}")

        self.original_address = original_address
        self.allocated_address = allocated_address

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
        """"""
        if cls.length is None:
            raise TypeError("Dynamic array has no static size")
        return cls.data_type.size() * cls.length

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int, length: int | None = None, deref_ptrs: bool = True):
        """"""
        if cls.length is None:
            if length is None:
                raise TypeError("Dynamic array requires a length argument")
            actual_len = length
        else:
            actual_len = cls.length

        items = []

        kind = None
        for flag, k in [
            ('is_primitive', 'primitive'),
            ('is_bitfield', 'bitfield'),
            ('is_union', 'union'),
            ('is_array', 'array'),
            ('is_struct', 'struct'),
            ('is_pointer', 'pointer'),
        ]:
            if getattr(cls.data_type, flag, False):
                kind = k
                break

        if kind is None:
            raise TypeError(f"Unsupported array element type {cls.data_type}")

        handler = FROM_BYTES_HANDLERS[kind]
        size = cls.data_type.size() if kind not in ('array', 'struct', 'union') else None

        for i in range(actual_len):
            item_offset = offset + i * (size or 0)
            item = handler(cls.data_type, buffer, item_offset, deref_ptrs=deref_ptrs)# cls.data_type.from_bytes(buffer, item_offset)
            items.append(item)

        return cls(items, offset)

    def dyna_size(self):
        """"""
        return len(self.items) * self.data_type.size()

    def to_bytes(self):
        """"""
        data = bytearray(self.dyna_size())
        offset = 0

        for v in self.items:
            if hasattr(v, 'is_primitive'):
                b = self.data_type.to_bytes(v)
            else:
                b = v.to_bytes()
            data[offset:offset + len(b)] = b
            offset += len(b)

        return bytes(data)
