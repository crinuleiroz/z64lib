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

from z64lib.core.helpers import safe_enum, make_property


class FieldType:
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

    def from_bytes(self, buffer: bytes, offset: int):
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

    @staticmethod
    def _align_to(offset: int, align: int) -> int:
        if align == 0:
            return offset
        return (offset + align -1) & ~(align -1) # (offset + align - 1) // align * align

    @classmethod
    def from_bytes(cls, buffer: bytes, struct_offset: int = 0):
        """
        Instantiates a struct object from binary data.

        Args:
            buffer: Binary struct data.
            struct_offset: Struct offset in binary data.

        Returns:
            object: A fully instantiated struct object.
        """
        obj = cls.__new__(cls)
        field_offset = struct_offset
        bit_cursor = 0
        last_bitfield_type = None

        for field in cls._fields_:
            match len(field):
                case 2:
                    name, field_type = field

                    # Reset bitfield tracking
                    bit_cursor = 0
                    last_bitfield_type = None

                    field_offset = cls._align_to(field_offset, cls._align_)
                    value, size = cls._read_field(buffer, field_offset, field_type)
                    setattr(obj, name, value)
                    field_offset += size

                case 3:
                    name, container_type, subfields = field
                    if isinstance(subfields, list):
                        values = {}
                        base_type = subfields[0][1]
                        bit_cursor = 0
                        for subname, sub_type, sub_bits in subfields:
                            assert sub_type == base_type, "Grouped bitfields must use the same base type."
                            bitfield_type = bitfield(sub_type, sub_bits)
                            bitfield_value = bitfield_type.from_bytes(buffer, field_offset, bit_cursor)
                            values[subname] = bitfield_value
                            bit_cursor += sub_bits

                        setattr(obj, name, container_type(**values))
                        field_offset += base_type.size
                        bit_cursor = 0
                        last_bitfield_type = None
                    else:
                        name, base_type, bit_width = field
                        if last_bitfield_type != base_type:
                            bit_cursor = 0
                            last_bitfield_type = base_type

                        bitfield_type = bitfield(base_type, bit_width)
                        bitfield_value = bitfield_type.from_bytes(buffer, field_offset, bit_cursor)
                        setattr(obj, name, bitfield_value)

                        bit_cursor += bit_width
                        if bit_cursor >= base_type.size * 8:
                            field_offset += base_type.size
                            bit_cursor = 0
                            last_bitfield_type = None

        for bool_field in getattr(cls, '_bool_fields_', []):
            raw_value = getattr(obj, bool_field)
            setattr(obj, f'_{bool_field}_raw', raw_value)

            if not hasattr(cls, bool_field):
                setattr(cls, bool_field, make_property(bool_field, bool))

        for enum_field, enum_type in getattr(cls, '_enum_fields_', {}).items():
            raw_value = getattr(obj, enum_field)
            setattr(obj, f'_{enum_field}_raw', raw_value)

            if not hasattr(cls, enum_field):
                transform = (lambda t: (lambda val: safe_enum(t, val)))(enum_type)
                setattr(cls, enum_field, make_property(enum_field, transform))
        return obj

    @classmethod
    def size(cls):
        size = 0
        for f in cls._fields_:
            match len(f):
                case 2:
                    _, field_type = f

                    if inspect.isclass(field_type) and issubclass(field_type, Z64Struct):
                        size += field_type.size()
                    elif isinstance(field_type, pointer):
                        size += 4
                    elif isinstance(field_type, array):
                        size += field_type.size
                    else:
                        size += field_type.size

                case 3:
                    if isinstance(f[2], list):
                        _, _, subfields = f
                        size += subfields[0][1].size
                    else:
                        continue
        return size

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
