import hashlib
import struct
from z64lib.types.base import DataType
from z64lib.types.markers import *
from z64lib.types.composites import array, bitfield
from z64lib.types.references import pointer
from z64lib.types._internals import walk_fields


class Z64Struct(DataType, StructType):
    """
    Base class for Zelda64 binary structures.

    Subclasses define a `_fields_` list of (name, type) pairs, similar to ctypes.structures,
    and can be parsed directly from bytes using `Z64Struct.from_bytes()`.
    """
    _fields_: list[tuple[str, DataType] | tuple[str, DataType, int]] | list[tuple[str, DataType, tuple[str, DataType, int]]] = []
    _bool_fields_: list[str] = []
    _enum_fields_: dict[str, type] = {} # field name -> enum
    _align_: int = 1

    @classmethod
    def size(cls) -> int:
        """ Returns the total size of the structure in bytes. """
        def callback(name, data_type, offset, extra):
            # Grouped bitfields
            if extra:
                base_type = extra[0][1]
                return offset + base_type.size()

            # Everything else
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