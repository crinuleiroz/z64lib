"""
z64lib.core.types
=====

A ctypes-like system for defining and parsing Zelda64 binary structs.
"""
import struct
import inspect
import hashlib
from typing import Type, Any
from dataclasses import dataclass

from z64lib.core._accessors import UnionAccessor
from z64lib.core._internals import walk_fields
from z64lib.core.alignment import align_to


#region Struct Field Type Classes
class FieldType:
    """ Base class all struct types inherit their properties from. """
    size: int = 0
    signed: bool

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int) -> Any:
        raise NotImplementedError

    def to_bytes(self, value) -> bytes:
        raise NotImplementedError


class u8(FieldType):
    """ An unsigned 8-bit integer. """
    size: int = 1
    signed: bool = False

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        return struct.unpack_from('>B', buffer, offset)[0]

    @classmethod
    def to_bytes(cls, value):
        return struct.pack('>B', value)


class s8(FieldType):
    """ A signed 8-bit integer. """
    size: int = 1
    signed: bool = True

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        return struct.unpack_from('>b', buffer, offset)[0]

    @classmethod
    def to_bytes(cls, value):
        return struct.pack('>b', value)


class u16(FieldType):
    """ An unsigned 16-bit integer. """
    size: int = 2
    signed: bool = False

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        return struct.unpack_from('>H', buffer, offset)[0]

    @classmethod
    def to_bytes(cls, value):
        return struct.pack('>H', value)


class s16(FieldType):
    """ A signed 16-bit integer. """
    size: int = 2
    signed: bool = True

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        return struct.unpack_from('>h', buffer, offset)[0]

    @classmethod
    def to_bytes(cls, value):
        return struct.pack('>h', value)


class u32(FieldType):
    """ An unsigned 32-bit integer. """
    size: int = 4
    signed: bool = False

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        return struct.unpack_from('>I', buffer, offset)[0]

    @classmethod
    def to_bytes(cls, value):
        return struct.pack('>I', value)


class s32(FieldType):
    """ A signed 32-bit integer. """
    size: int = 4
    signed: bool = True

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        return struct.unpack_from('>i', buffer, offset)[0]

    @classmethod
    def to_bytes(cls, value):
        return struct.pack('>i', value)


class f32(FieldType):
    """ A 32-bit single-precision floating-point value. """
    size: int = 4
    signed: bool = True

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        return struct.unpack_from('>f', buffer, offset)[0]

    @classmethod
    def to_bytes(cls, value):
        return struct.pack('>f', value)


class pointer(FieldType):
    """ An unsigned 32-bit integer that indicates an offset to a new structure in the binary data. """
    def __init__(self, struct_type: Type['Z64Struct']):
        self.struct_type: Type['Z64Struct'] = struct_type
        self.size: int = 4

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
            obj._original_address = addr
            return obj
        except Exception as e:
            print(f"warning: failed to parse {self.struct_type.__name__} at 0x{addr:X}: {e}")
            return None

    def to_bytes(self, value):
        if not value:
            return struct.pack('>I', 0)

        addr = getattr(value, '_address', None)
        if addr is None:
            addr = getattr(value, '_original_addresss', 0)

        return struct.pack('>I', addr)


class array(FieldType):
    """ Represents a fixed-size array of field types. """
    def __init__(self, field_type: Type['FieldType'], length: int):
        self.field_type = field_type
        self.length = length
        self.items = []

    @property
    def size(self):
        return self.field_type.size * self.length

    @property
    def signed(self):
        return getattr(self.field_type, 'signed', False)

    def from_bytes(self, buffer: bytes, offset: int):
        self.items = []

        for i in range(self.length):
            item_offset = offset + i * self.field_type.size
            item = self.field_type.from_bytes(buffer, item_offset)
            self.items.append(item)

        return self

    def to_bytes(self, values):
        data = bytearray()

        for v in values:
            data += self.field_type.to_bytes(v)

        return bytes(data)

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


class bitfield(FieldType):
    """ A number of bits that represent a single field in a struct. """
    _FMT_MAP = {
        1: ('>B', '>b'),
        2: ('>H', '>h'),
        4: ('>I', '>i'),
    }

    def __init__(self, field_type, bit_width):
        self.field_type = field_type
        self.bit_width = bit_width

    @property
    def size(self):
        return self.field_type.size

    @property
    def signed(self):
        return self.field_type.signed

    def _fmt(self):
        return self._FMT_MAP[self.size][1 if self.signed else 0]

    def from_bytes(self, buffer: bytes, offset: int, bit_cursor: int):
        format = self._fmt()

        # Extracts bits from the structure, then performs the relevant operations
        # to split the specified bit into a separate attribute for the object.
        bits = struct.unpack_from(format, buffer, offset)[0]
        bit_shift = self.size * 8 - bit_cursor - self.bit_width
        bit_mask = (1 << self.bit_width) - 1
        bit_value = (bits >> bit_shift) & bit_mask

        # Sign extension
        if self.signed and (bit_value & (1 << (self.bit_width - 1))):
            bit_value -= (1 << self.bit_width)

        return bit_value

    def to_bytes(self, bit_value: int, bit_cursor: int, base_value: int = 0) -> tuple[bytes, int]:
        format = self._fmt()

        # Pack the bits back into a single value.
        bit_shift = self.size * 8 - bit_cursor - self.bit_width
        bit_mask = (1 << self.bit_width) - 1
        bits = base_value | ((bit_value & bit_mask) << bit_shift)

        return struct.pack(format, bits), bits


class union(FieldType):
    """ A struct member whose memory is shared by multiple values. """
    def __init__(self, *fields):
        self._fields = fields

    @property
    def size(self):
        sizes = []

        for name, field_type in self._fields:
            if inspect.isclass(field_type) and issubclass(field_type, Z64Struct):
                sizes.append(field_type.size_class())
            else:
                sizes.append(getattr(field_type, 'size', 0))

        return max(sizes)

    def from_bytes(self, buffer: bytes | bytearray, offset: int):
        values = {}

        for name, field_type in self._fields:
            if inspect.isclass(field_type) and issubclass(field_type, Z64Struct):
                values[name] = field_type.from_bytes(buffer, offset)
            else:
                values[name] = field_type.from_bytes(buffer, offset)

        return UnionAccessor(values)

    def to_bytes(self, accessor: UnionAccessor) -> bytes:
        active_name = accessor.active_field
        if active_name not in accessor._values:
            raise ValueError()

        value = accessor._values[active_name]
        field_type = None
        for name, f_type in self._fields:
            if name == active_name:
                field_type = f_type
                break

        if field_type is None:
            raise ValueError()

        if inspect.isclass(field_type) and issubclass(field_type, Z64Struct):
            return value.to_bytes()
        else:
            return field_type.to_bytes(value)
#endregion


#region Base Struct Classes
class Z64Struct:
    """
    Base class for Zelda64 binary structures.

    Subclasses define a `_fields_` list of (name, type) pairs, similar to ctypes.structures,
    and can be parsed directly from bytes using `Z64Struct.from_bytes()`.
    """
    _fields_: list[tuple[str, Any] | tuple[str, Any, int]] | list[tuple[str, Any, tuple[str, Any, int]]] = []
    _bool_fields_: list[str] = []
    _enum_fields_: dict[str, type] = {} # field name -> enum
    _align_: int = 1

    @staticmethod
    def _read_field(buffer: bytes, field_offset: int, field_type: Any) -> tuple[Any, int]:
        # Embedded structure
        if inspect.isclass(field_type) and issubclass(field_type, Z64Struct):
            value = field_type.from_bytes(buffer, field_offset)
            size = field_type.size()

        # Pointer
        elif isinstance(field_type, pointer):
            value = field_type.from_bytes(buffer, field_offset)
            size = field_type.size

        # Primitive
        else:
            value = field_type.from_bytes(buffer, field_offset)
            size = field_type.size

        return value, size

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

        def callback(name, field_type, offset, extra):
            if extra: # Grouped bitfields
                values = {}
                base_type = extra[0][1]
                bit_cursor = 0
                for subname, sub_type, sub_bits in extra:
                    bf_type = bitfield(sub_type, sub_bits)
                    bf_value = bf_type.from_bytes(buffer, offset, bit_cursor)
                    values[subname] = bf_value
                    bit_cursor += sub_bits
                setattr(obj, name, field_type(**values))
                return offset + base_type.size

            elif isinstance(field_type, bitfield):
                raise NotImplementedError()
            else:
                value = field_type.from_bytes(buffer, offset)
                setattr(obj, name, value)

                if callable(getattr(field_type, 'size', None)):
                    size = field_type.size_class()
                else:
                    size = getattr(field_type, 'size', 0)

                return offset + size

        walk_fields(cls._fields_, callback, struct_offset)
        return obj

    def to_bytes(self) -> bytes:
        """ Compiles a struct object from memory into binary data. """
        buffer = bytearray(self.size())

        def callback(name, field_type, offset, extra):
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
                buffer[offset:offset + base_type.size] = base_type.to_bytes(bits)
                return offset + base_type.size

            # Boolean field
            if name in getattr(self, "_bool_fields_", []):
                value = 1 if value else 0

            # Array
            if isinstance(field_type, array):
                size = len(value) * field_type.field_type.size
                buffer[offset:offset + size] = field_type.to_bytes(value)
                return offset + size

            # Pointer
            if isinstance(field_type, pointer):
                buffer[offset:offset + field_type.size] = field_type.to_bytes(value)
                return offset + field_type.size

            # Nested struct
            if isinstance(value, Z64Struct):
                buffer[offset:offset + value.size()] = value.to_bytes()
                return offset + value.size()

            # Primitive
            buffer[offset:offset + field_type.size] = field_type.to_bytes(value)
            return offset + field_type.size

        walk_fields(self._fields_, callback)
        return bytes(buffer)

    @classmethod
    def size_class(cls) -> int:
        """ Returns the total size of the structure in bytes. """
        def callback(name, field_type, offset, extra):
            # Nested structs
            if inspect.isclass(field_type) and issubclass(field_type, Z64Struct):
                return offset + field_type.size_class()

            # Grouped bitfields
            elif extra:
                base_type = extra[0][1]
                return offset + base_type.size

            # Primitives, pointers, and arrays
            return offset + getattr(field_type, 'size', 0)

        offset = walk_fields(cls._fields_, callback)
        if getattr(cls, '_align_', 1) > 1:
            offset = align_to(offset, cls._align_)
        return offset

    def size(self) -> int:
        return self.__class__.size_class()

    def _stable_bytes(self) -> bytes:
        buffer = bytearray()

        def callback(name, field_type, offset, extra):
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
                return offset + base_type.size

            if name in getattr(self, '_bool_fields_', []):
                value = 1 if value else 0

            if isinstance(field_type, array):
                buffer.extend(field_type.to_bytes(value))
                return offset + len(value) * field_type.field_type.size

            if isinstance(field_type, pointer):
                buffer.extend(struct.pack('>I', 0xFFFFFFFF))
                return offset + 4

            if isinstance(value, Z64Struct):
                buffer.extend(value._stable_bytes())
                return offset + value.size()

            buffer.extend(field_type.to_bytes(value))
            return offset + field_type.size

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

        def callback(name, field_type, offset, extra):
            value = getattr(obj, name, None)

            # Nested structs
            if isinstance(value, Z64Struct):
                return offset + value.size()

            # Grouped bitfields
            if extra:
                base_type = extra[0][1]
                return offset + base_type.size

            # Primitives, pointers, and arrays
            if isinstance(field_type, array):
                if value is not None:
                    return offset + len(value) * field_type.field_type.size
                return offset + getattr(field_type, 'size', 0)

            return offset + getattr(field_type, 'size', 0)

        offset = walk_fields(self._fields_, callback)
        return align_to(offset, getattr(self, '_align_', 1))
#endregion