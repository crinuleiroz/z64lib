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

        def callback(name, data_type, offset):

            if issubclass(data_type, BitfieldType):
                value = data_type.from_bytes(buffer, offset)
                offset += data_type.size()

                for sub_name in cls._bool_fields_:
                    if hasattr(value, sub_name):
                        setattr(value, sub_name, bool(getattr(value, sub_name)))
                for sub_name, enum_type in cls._enum_fields_.items():
                    if hasattr(value, sub_name):
                        setattr(value, sub_name, enum_type(getattr(value, sub_name)))

            elif issubclass(data_type, UnionType):
                value = data_type.from_bytes(buffer, offset)
                offset += data_type.size()

            elif issubclass(data_type, PointerType):
                value = data_type.from_bytes(buffer, offset)
                offset += data_type.size()

            elif issubclass(data_type, ArrayType) and data_type.length is None:
                value = None

            else:
                value = data_type.from_bytes(buffer, offset)
                offset += data_type.size()

                if name in cls._bool_fields_:
                    value = bool(value)

                enum_type = cls._enum_fields_.get(name)
                if enum_type is not None:
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

            # Boolean field
            if name in getattr(self, '_bool_fields_', []):
                value = 1 if value else 0

            enum_type = self._enum_fields_.get(name)
            if enum_type is not None and isinstance(value, IntEnum):
                value = value.value

            if issubclass(data_type, BitfieldType):
                field_dict = {}
                for f_name, width in data_type.fields:
                    val = getattr(value, f_name)
                    if f_name in self._bool_fields_:
                        val = 1 if val else 0
                    enum_type = self._enum_fields_.get(f_name)
                    if enum_type is not None and isinstance(val, IntEnum):
                        val = val.value
                    field_dict[f_name] = val
                buffer[offset:offset + data_type.size()] = data_type.to_bytes(field_dict)
                return offset + data_type.size()

            if issubclass(data_type, UnionType):
                buffer[offset:offset + data_type.size()] = value.to_bytes()
                return offset + data_type.size()

            # Array
            if issubclass(data_type, ArrayType):
                if data_type.length is None:
                    raise TypeError(f"Dynamic array field '{name}' must be serialized manually.")
                buffer[offset:offset + data_type.size()] = data_type.to_bytes(value)
                return offset + data_type.size()

            # if issubclass(data_type, ArrayType) and data_type.length is None:
            #     return offset

            # Pointer
            if issubclass(data_type, PointerType):
                buffer[offset:offset + data_type.size()] = data_type.to_bytes(value)
                return offset + data_type.size()

            # Struct
            if isinstance(value, Z64Struct):
                buffer[offset:offset + value.size()] = value.to_bytes()
                return offset + value.size()

            # Primitive
            buffer[offset:offset + data_type.size()] = data_type.to_bytes(value)
            return offset + data_type.size()

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

            if name in getattr(self, '_bool_fields_', []):
                value = 1 if value else 0

            enum_type = self._enum_fields_.get(name)
            if enum_type is not None and isinstance(value, IntEnum):
                value = value.value

            if issubclass(data_type, BitfieldType):
                field_dict = {}
                for f_name, width in data_type.fields:
                    val = getattr(value, f_name)
                    if f_name in self._bool_fields_:
                        val = 1 if val else 0
                    enum_type = self._enum_fields_.get(f_name)
                    if enum_type is not None and isinstance(val, IntEnum):
                        val = val.value
                    field_dict[f_name] = val
                buffer[offset:offset + data_type.size()] = data_type.to_bytes(field_dict)
                return offset + data_type.size()

            if issubclass(data_type, UnionType):
                buffer.extend(value.to_bytes())
                return offset + data_type.size()

            if issubclass(data_type, ArrayType):
                buffer.extend(data_type.to_bytes(value))
                return offset + len(value) * data_type.data_type.size()

            if issubclass(data_type, PointerType):
                buffer.extend(struct.pack('>I', 0xFFFFFFFF))
                return offset + 4

            if isinstance(value, Z64Struct):
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
            name = field[0]
            value = getattr(self, name)
            if isinstance(value, Z64Struct):
                value_repr = repr(value).replace('\n', '\n  ')
                lines.append(f'  {name}={value_repr}')
            else:
                lines.append(f'  {name}={value}')
        lines.append(')')

        return '\n'.join(lines)