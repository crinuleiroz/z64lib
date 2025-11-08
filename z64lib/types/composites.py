import hashlib
import inspect
import struct
from ._accessors import UnionAccessor
from ._internals import walk_fields
from z64lib.types import DataType
from z64lib.types import pointer


#region Array
class array(DataType):
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

#endregion


#region bitfield
class bitfield(DataType):
    """ A number of bits that represent a single field in a struct. """
    _FMT_MAP = {
        1: ('>B', '>b'),
        2: ('>H', '>h'),
        4: ('>I', '>i'),
    }

    def __init__(self, data_type, bit_width):
        self.data_type = data_type
        self.bit_width = bit_width

    @property
    def signed(self):
        return self.data_type.signed

    def size(self):
        return self.data_type.size()

    def _fmt(self):
        return self._FMT_MAP[self.size()][1 if self.signed else 0]

    def from_bytes(self, buffer: bytes, offset: int, bit_cursor: int):
        format = self._fmt()

        # Extracts bits from the structure, then performs the relevant operations
        # to split the specified bit into a separate attribute for the object.
        bits = struct.unpack_from(format, buffer, offset)[0]
        bit_shift = self.size() * 8 - bit_cursor - self.bit_width
        bit_mask = (1 << self.bit_width) - 1
        bit_value = (bits >> bit_shift) & bit_mask

        # Sign extension
        if self.signed and (bit_value & (1 << (self.bit_width - 1))):
            bit_value -= (1 << self.bit_width)

        return bit_value

    def to_bytes(self, bit_value: int, bit_cursor: int, base_value: int = 0) -> tuple[bytes, int]:
        format = self._fmt()

        # Pack the bits back into a single value.
        bit_shift = self.size() * 8 - bit_cursor - self.bit_width
        bit_mask = (1 << self.bit_width) - 1
        bits = base_value | ((bit_value & bit_mask) << bit_shift)

        return struct.pack(format, bits), bits

#endregion


#region Union
class union(DataType):
    """ A struct member whose memory is shared by multiple values. """
    def __init__(self, *fields):
        self._fields = fields

    def size(self):
        sizes = []

        for name, data_type in self._fields:
            if inspect.isclass(data_type) and issubclass(data_type, Z64Struct):
                sizes.append(data_type.size_class())
            else:
                sizes.append(data_type.size())

        return max(sizes)

    def from_bytes(self, buffer: bytes | bytearray, offset: int):
        values = {}

        for name, data_type in self._fields:
            if inspect.isclass(data_type) and issubclass(data_type, Z64Struct):
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

        if inspect.isclass(data_type) and issubclass(data_type, Z64Struct):
            return value.to_bytes()
        else:
            return data_type.to_bytes(value)
#endregion


#region Structs
class Z64Struct(DataType):
    """
    Base class for Zelda64 binary structures.

    Subclasses define a `_fields_` list of (name, type) pairs, similar to ctypes.structures,
    and can be parsed directly from bytes using `Z64Struct.from_bytes()`.
    """
    _fields_: list[tuple[str, DataType] | tuple[str, DataType, int]] | list[tuple[str, DataType, tuple[str, DataType, int]]] = []
    _bool_fields_: list[str] = []
    _enum_fields_: dict[str, type] = {} # field name -> enum
    _align_: int = 1

    def size(self) -> int:
        return self.size_class()

    @classmethod
    def size_class(cls) -> int:
        """ Returns the total size of the structure in bytes. """
        def callback(name, data_type, offset, extra):
            # Nested structs
            if inspect.isclass(data_type) and issubclass(data_type, Z64Struct):
                return offset + data_type.size_class()

            # Grouped bitfields
            if extra:
                base_type = extra[0][1]
                return offset + base_type.size()

            # Primitives, pointers, and arrays
            return offset + data_type.size()

        offset = walk_fields(cls._fields_, callback)
        if getattr(cls, '_align_', 1) > 1:
            offset = cls.align_to(offset, cls._align_)
        return offset

    @classmethod
    def from_bytes(cls, buffer: bytes, struct_offset: int = 0):
        """
        Instantiates a struct object from binary data.

        Parameters
        ----------
        buffer: bytes
            Binary struct data.
        struct_offset: int
            Offset to the struct.

        Returns
        ----------
        object
            Returns a fully instantiated object of the inheritor.
        """
        obj = cls.__new__(cls)

        def callback(name, data_type, offset, extra):
            if extra: # Grouped bitfields
                values = {}
                base_type = extra[0][1]
                bit_cursor = 0
                for subname, sub_type, sub_bits in extra:
                    bf_type = bitfield(sub_type, sub_bits)
                    bf_value = bf_type.from_bytes(buffer, offset, bit_cursor)
                    values[subname] = bf_value
                    bit_cursor += sub_bits
                setattr(obj, name, data_type(**values))
                return offset + base_type.size()

            elif isinstance(data_type, bitfield):
                raise NotImplementedError()
            else:
                value = data_type.from_bytes(buffer, offset)
                setattr(obj, name, value)

                if inspect.isclass(data_type) and issubclass(data_type, Z64Struct):
                    size = data_type.size_class()
                else:
                    size = data_type.size()

                return offset + size

        walk_fields(cls._fields_, callback, struct_offset)
        return obj

    def to_bytes(self) -> bytes:
        """ Compiles a struct object from memory into binary data. """
        buffer = bytearray(self.size())

        def callback(name, data_type, offset, extra):
            value = getattr(self, name)

            # Bitfield group
            if extra:
                base_type = extra[0][1]
                bits = 0
                bit_cursor = 0
                for sub_name, sub_type, sub_bits in extra:
                    sub_val = getattr(value, sub_name)
                    bf = bitfield(sub_type, sub_bits)
                    bf_bytes, bits = bf.to_bytes(sub_val, bit_cursor, bits)
                    bit_cursor += sub_bits
                buffer[offset:offset + base_type.size()] = base_type.to_bytes(bits)
                return offset + base_type.size()

            # Boolean field
            if name in getattr(self, "_bool_fields_", []):
                value = 1 if value else 0

            # Array
            if isinstance(data_type, array):
                size = len(value) * data_type.data_type.size()
                buffer[offset:offset + size] = data_type.to_bytes(value)
                return offset + size

            # Pointer
            if isinstance(data_type, pointer):
                buffer[offset:offset + data_type.size()] = data_type.to_bytes(value)
                return offset + data_type.size()

            # Nested struct
            if isinstance(value, Z64Struct):
                buffer[offset:offset + value.size()] = value.to_bytes()
                return offset + value.size()

            # Primitive
            buffer[offset:offset + data_type.size()] = data_type.to_bytes(value)
            return offset + data_type.size()

        walk_fields(self._fields_, callback)
        return bytes(buffer)

    @staticmethod
    def _read_field(buffer: bytes, offset: int, data_type: DataType) -> tuple[DataType, int]:
        # Embedded structure
        offset = Z64Struct.align_field(offset, data_type)

        value = data_type.from_bytes(buffer, offset)
        size = data_type.size()

        # if inspect.isclass(data_type) and issubclass(data_type, Z64Struct):
        #     value = data_type.from_bytes(buffer, field_offset)
        #     size = data_type.size()

        # # Pointer
        # elif isinstance(data_type, pointer):
        #     value = data_type.from_bytes(buffer, field_offset)
        #     size = data_type.size()

        # # Primitive
        # else:
        #     value = data_type.from_bytes(buffer, field_offset)
        #     size = data_type.size()

        return value, size

    def _stable_bytes(self) -> bytes:
        buffer = bytearray()

        def callback(name, data_type, offset, extra):
            value = getattr(self, name)

            if extra:
                base_type = extra[0][1]
                bits = 0
                bit_cursor = 0
                for sub_name, sub_type, sub_bits in extra:
                    sub_val = getattr(value, sub_name)
                    bf = bitfield(sub_type, sub_bits)
                    bf_bytes, bits = bf.to_bytes(sub_val, bit_cursor, bits)
                    bit_cursor += sub_bits
                buffer.extend(base_type.to_bytes(bits))
                return offset + base_type.size()

            if name in getattr(self, '_bool_fields_', []):
                value = 1 if value else 0

            if isinstance(data_type, array):
                buffer.extend(data_type.to_bytes(value))
                return offset + len(value) * data_type.data_type.size()

            if isinstance(data_type, pointer):
                buffer.extend(struct.pack('>I', 0xFFFFFFFF))
                return offset + 4

            if isinstance(value, Z64Struct):
                buffer.extend(value._stable_bytes())
                return offset + value.size()

            buffer.extend(data_type.to_bytes(value))
            return offset + data_type.size()

        walk_fields(self._fields_, callback)
        return bytes(buffer)

    def get_hash(self):
        """ Return a stable SHA-256 hash as an integer. """
        return int(hashlib.sha256(self._stable_bytes()).hexdigest(), 16)

    def __repr__(self):
        lines = [f'{type(self).__name__}(']

        for field in self._fields_:
            name = field[0]
            value = getattr(self, name)
            if isinstance(value, Z64Struct):
                value_repr = repr(value).replace('\n', '\n  ')
                lines.append(f'  {name}={value_repr}')
            else:
                lines.append(f'  {name}={value}')
        lines.append(')')

        return '\n'.join(lines)


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
#endregion