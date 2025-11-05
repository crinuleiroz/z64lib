"""
z64lib.core.types
=====

A ctypes-like system for defining and parsing Zelda64 binary structures.

Provides primitive field types (u8, s8, u16, s16, u32, s32, f32, pointer, array, bitfield)
and a base class `Z64Struct` that supports aligned, nested structure parsing from big-endian data.
"""
import struct
import inspect
from typing import Type, Any
from dataclasses import dataclass

from z64lib.core.alignment import walk_fields, align_to
from z64lib.core.helpers import safe_enum, make_property


class FieldType:
    """ Base class all struct types inherit their properties from. """
    size: int = 0
    signed: bool

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int) -> Any:
        raise NotImplementedError


class u8(FieldType):
    """ An unsigned 8-bit integer. """
    size: int = 1
    signed: bool = False

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        return struct.unpack_from('>B', buffer, offset)[0]


class s8(FieldType):
    """ A signed 8-bit integer. """
    size: int = 1
    signed: bool = True

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        return struct.unpack_from('>b', buffer, offset)[0]


class u16(FieldType):
    """ An unsigned 16-bit integer. """
    size: int = 2
    signed: bool = False

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        return struct.unpack_from('>H', buffer, offset)[0]


class s16(FieldType):
    """ A signed 16-bit integer. """
    size: int = 2
    signed: bool = True

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        return struct.unpack_from('>h', buffer, offset)[0]


class u32(FieldType):
    """ An unsigned 32-bit integer. """
    size: int = 4
    signed: bool = False

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        return struct.unpack_from('>I', buffer, offset)[0]


class s32(FieldType):
    """ A signed 32-bit integer. """
    size: int = 4
    signed: bool = True

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        return struct.unpack_from('>i', buffer, offset)[0]


class f32(FieldType):
    """ A 32-bit single-precision floating-point value. """
    size: int = 4
    signed: bool = True

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        return struct.unpack_from('>f', buffer, offset)[0]


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
            If the address is 0, returns None instead.
        """
        addr = struct.unpack_from('>I', buffer, offset)[0]

        if addr == 0:
            return None

        return self.struct_type.from_bytes(buffer, addr)


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


@dataclass
class bitfield(FieldType):
    """ A number of bits that represent a single field in a struct. """
    field_type: Type[FieldType]
    bit_width: int

    @property
    def size(self):
        return self.field_type.size

    @property
    def signed(self):
        return self.field_type.signed

    def from_bytes(self, buffer: bytes, offset: int, bit_cursor: int):
        format = {
            1: '>B' if not self.signed else '>b',
            2: '>H' if not self.signed else '>h',
            4: '>I' if not self.signed else '>i',
        }.get(self.size)

        if format is None:
            raise ValueError(f'Unsupported bitfield base size: {self.size}')

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