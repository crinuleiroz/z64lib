from enum import IntEnum
import hashlib
import struct
from z64lib.types.base import DataType
from z64lib.types.markers import *


class Z64Struct(DataType, StructType):
    """
    Base class for Zelda64 binary structures.

    Subclasses define a `_fields_` list of (name, type) pairs, similar to ctypes.structures,
    and can be parsed directly from bytes using `Z64Struct.from_bytes()`.
    """
    _fields_: list[tuple[str, DataType]] = []
    _bool_fields_: list[str] = []
    _enum_fields_: dict[str, type] = {} # field name -> enum
    _align_: int = 1

    @classmethod
    def size(cls) -> int:
        """ Returns the total size of the structure in bytes. """
        def callback(name, data_type, offset):
            return offset + data_type.size()

        offset = cls.walk_fields(cls._fields_, callback)

        if cls._align_ > 1:
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

        def callback(name, data_type, offset):
            value = None
            enum_type = cls._enum_fields_.get(name)

            # Primitive
            if issubclass(data_type, PrimitiveType):
                value = data_type.from_bytes(buffer, offset)
                offset += data_type.size()

            # Bitfield
            if issubclass(data_type, BitfieldType):
                value = data_type.from_bytes(buffer, offset)
                offset += data_type.size()

                for sub_name in cls._bool_fields_:
                    if hasattr(value, sub_name):
                        setattr(value, sub_name, bool(getattr(value, sub_name)))
                for sub_name, enum_type in cls._enum_fields_.items():
                    if hasattr(value, sub_name):
                        setattr(value, sub_name, enum_type(getattr(value, sub_name)))

            # Union
            if issubclass(data_type, UnionType):
                value = data_type.from_bytes(buffer, offset)
                offset += data_type.size()

            # Array
            if issubclass(data_type, ArrayType):
                if data_type.length is None:
                    value = None
                else:
                    value = data_type.from_bytes(buffer, offset)
                    offset += data_type.size()

            # Struct
            if issubclass(data_type, StructType):
                value = data_type.from_bytes(buffer, offset)
                offset += data_type.size()

            # Pointer
            if issubclass(data_type, PointerType):
                value = data_type.from_bytes(buffer, offset).deref(buffer)
                offset += data_type.size()

            # Bool field
            if (
                name in cls._bool_fields_
                and value is not None
            ):
                value = bool(value)

            # Enum field
            if (
                enum_type is not None
                and value is not None
                and not issubclass(data_type, BitfieldType)
            ):
                value = enum_type(value)

            setattr(obj, name, value)
            return offset

        cls.walk_fields(cls._fields_, callback, struct_offset)
        return obj

    def to_bytes(self) -> bytes:
        """ Compiles a struct object from memory into binary data. """
        buffer = bytearray(self.size())

        def callback(name, data_type, offset):
            value = getattr(self, name)
            enum_type = self._enum_fields_.get(name)

            # Bool field
            if name in self._bool_fields_:
                value = 1 if value else 0

            # Enum field
            if (
                enum_type is not None
                and isinstance(value, IntEnum)
            ):
                value = value.value

            # Primitive
            if issubclass(data_type, PrimitiveType):
                buffer[offset:offset + data_type.size()] = data_type.to_bytes(value)
                return offset + data_type.size()

            # Bitfield
            if issubclass(data_type, BitfieldType):
                buffer[offset:offset + data_type.size()] = value.to_bytes()
                return offset + data_type.size()

            # Union
            if issubclass(data_type, UnionType):
                buffer[offset:offset + data_type.size()] = value.to_bytes()
                return offset + data_type.size()

            # Array
            if issubclass(data_type, ArrayType):
                if data_type.length is None:
                    if hasattr(value, 'to_bytes'):
                        dyn_bytes = value.to_bytes()
                        buffer[offset:offset + len(dyn_bytes)] = dyn_bytes
                        return offset + len(dyn_bytes)
                    else:
                        for i, item in enumerate(value):
                            buffer[offset:offset + data_type.data_type.size()] = data_type.data_type.to_bytes()
                            offset += data_type.data_type.size()
                        return offset
                else:
                    buffer[offset:offset + data_type.size()] = data_type.to_bytes(value)
                    return offset + data_type.size()

            # Struct
            if issubclass(data_type, StructType):
                buffer[offset:offset + value.size()] = value.to_bytes()
                return offset + value.size()

            # Pointer
            if issubclass(data_type, PointerType):
                if hasattr(value, 'obj'):
                    buffer[offset:offset + data_type.size()] = value.to_bytes()
                else:
                    temp_ptr = data_type(obj=value)
                    buffer[offset:offset + data_type.size()] = temp_ptr.to_bytes()
                return offset + data_type.size()

            raise TypeError()

        self.walk_fields(self._fields_, callback)
        return bytes(buffer)

    @staticmethod
    def _read_field(buffer: bytes, offset: int, data_type: DataType) -> tuple[DataType, int]:
        offset = data_type.align_field(offset, data_type)
        value = data_type.from_bytes(buffer, offset)
        size = data_type.size()
        return value, size

    @staticmethod
    def walk_fields(fields, callback, start_offset: int = 0) -> int:
        """
        Walks through the fields of a struct, calling `callback` for each field.

        Parameters
        ----------
        fields: list
            List of struct field definitions (_fields_).
        callback: Callable[[name, data_type, offset, extra], int]
            Function called for each field. Must return the new offset after processing.
        start_offset: int
            Starting offset.

        Returns
        ----------
        int
            Final offset after processing all fields.
        """
        offset = start_offset

        for field in fields:
            name, data_type = field
            offset = data_type.align_field(offset, data_type)
            offset = callback(name, data_type, offset)

        return offset

    def _stable_bytes(self) -> bytes:
        """"""
        buffer = bytearray()

        def callback(name, data_type, offset):
            value = getattr(self, name)
            enum_type = self._enum_fields_.get(name)

            if name in self._bool_fields_:
                value = 1 if value else 0

            if (
                enum_type is not None
                and isinstance(value, IntEnum)
            ):
                value = value.value

            if issubclass(data_type, BitfieldType):
                buffer.extend(value.to_bytes())
                return offset + data_type.size()

            if issubclass(data_type, UnionType):
                buffer.extend(value.to_bytes())
                return offset + data_type.size()

            if issubclass(data_type, ArrayType):
                buffer.extend(value.to_bytes())
                return offset + len(value) * data_type.data_type.size()

            if issubclass(data_type, PointerType):
                buffer.extend(struct.pack('>I', 0xFFFFFFFF))
                return offset + data_type.size()

            if issubclass(data_type, StructType):
                buffer.extend(value._stable_bytes())
                return offset + value.size()

            buffer.extend(data_type.to_bytes(value))
            return offset + data_type.size()

        self.walk_fields(self._fields_, callback)
        return bytes(buffer)

    def get_hash(self):
        """ Return a stable SHA-256 hash as an integer. """
        return int(hashlib.sha256(self._stable_bytes()).hexdigest(), 16)

    def __repr__(self):
        lines = [f'{type(self).__name__}(']

        for field in self._fields_:
            name, data_type = field
            value = getattr(self, name)

            if isinstance(value, Z64Struct):
                value_repr = repr(value).replace('\n', '\n  ')
            else:
                value_repr = repr(value)

            lines.append(f'  {name}={value_repr}')
        lines.append(')')

        return '\n'.join(lines)