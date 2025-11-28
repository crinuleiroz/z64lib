import hashlib
import struct
from z64lib.types.base import DataType, Field
from z64lib.types.markers import *


class Z64Struct(DataType, StructType):
    """ Static-sized Zelda64 struct. """
    _fields_: list[tuple[str, DataType]] = []
    _bools_: set[str] = set() # Set of field name
    _enums_: dict[str, type] = dict() # Dictionary of field name and enum class
    _align_: int = 1
    _layout_: list = None
    _struct_size_: int = 0

    is_dyna: bool = False

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if cls.is_dyna:
            return

        offset = 0
        layout = []

        for name, data_type in cls._fields_:
            if (
                issubclass(data_type, ArrayType)
                and data_type.length is None
            ): return

            field, offset = cls._describe_field(name, data_type, offset)
            layout.append(field)

        if cls._align_ > 1:
            offset = cls.align_to(offset, cls._align_)

        cls._layout_ = layout
        cls._struct_size_ = offset

    @classmethod
    def _describe_field(cls, name, data_type, offset, attr=None):
        """ Return (Field, new_offset) for one field. """
        offset = data_type.align_field(offset, data_type)

        if issubclass(data_type, PrimitiveType):
            size = data_type.size()
            kind = 'primitive'
        elif issubclass(data_type, BitfieldType):
            size = data_type.size()
            kind = 'bitfield'
        elif issubclass(data_type, UnionType):
            size = data_type.size()
            kind = 'union'
        elif issubclass(data_type, ArrayType):
            if data_type.length is None:
                size = (len(attr) * data_type.data_type.size()) if attr else 0
            else:
                size = data_type.size()
            kind = 'array'
        elif issubclass(data_type, StructType):
            if isinstance(attr, Z64Struct):
                size = attr.size()
            else:
                size = data_type.size()
            kind = 'struct'
        elif issubclass(data_type, PointerType):
            size = data_type.size()
            kind = 'pointer'
        else:
            raise TypeError()

        enum_cls = cls._enums_.get(name)
        is_bool = name in cls._bools_
        field = Field(name, data_type, offset, size, kind, enum_cls, is_bool)

        return field, offset + size

    @classmethod
    def size(cls) -> int:
        """ Returns the total size of the structure in bytes. """
        return cls._struct_size_

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int = 0):
        """"""
        obj = cls.__new__(cls)
        layout = cls._layout_ or obj._generate_layout()

        for field in layout:
            if not isinstance(field, Field):
                raise TypeError(f"Expected Field, got {type(field)}")

            field_offset = offset + field.offset

            T = field.type
            if issubclass(T, PrimitiveType):
                attr = T.from_bytes(buffer, field_offset)
            elif issubclass(T, BitfieldType):
                attr = T.from_bytes(buffer, field_offset, cls._bools_, cls._enums_)
            elif issubclass(T, StructType):
                attr = T.from_bytes(buffer, field_offset)
            elif issubclass(T, ArrayType):
                if T.length is None:
                    raise TypeError(f"Dynamic array '{field.name}' requires manual length")
                attr = T.from_bytes(buffer, field_offset)
            elif issubclass(T, PointerType):
                attr = T.from_bytes(buffer, field_offset).dereference(buffer)
            elif issubclass(T, UnionType):
                attr = T.from_bytes(buffer, field_offset)
            else:
                raise TypeError(f"Unsupported field type: {T}")

            attr = cls._normalize_in(attr, field)
            setattr(obj, field.name, attr)

        return obj

    def to_bytes(self) -> bytes:
        """"""
        buffer = bytearray(self.size())
        layout = self._layout_ or self._generate_layout()

        for field in layout:
            if not isinstance(field, Field):
                raise TypeError(f"Expected Field, got {type(field)}")

            attr = getattr(self, field.name)
            attr = self._normalize_out(attr, field)

            T = field.type
            if issubclass(T, PrimitiveType):
                b = T.to_bytes(attr)
            elif issubclass(T, BitfieldType):
                b = attr.to_bytes(self._bools_, self._enums_)
            elif issubclass(T, (UnionType, ArrayType, StructType)):
                b = attr.to_bytes()
            elif issubclass(T, PointerType):
                if attr is None:
                    b = struct.pack('>I', 0x00000000)
                elif isinstance(attr, T):
                    b = attr.to_bytes()
                else:
                    b = T(obj=attr).to_bytes()
            else:
                raise TypeError(f"Unsupported field type: {T}")

            buffer[field.offset:field.offset + len(b)] = b

        return bytes(buffer)

    @classmethod
    def _normalize_in(cls, attr, field: Field):
        """"""
        if issubclass(field.type, BitfieldType):
            return attr.normalize_in(cls._bools_, cls._enums_)
        if field.bool:
            return bool(attr)
        if field.enum and not isinstance(attr, field.enum):
            return field.enum(attr)
        return attr

    @classmethod
    def _normalize_out(cls, attr, field: Field):
        """"""
        if issubclass(field.type, BitfieldType):
            return attr.normalize_out(cls._bools_, cls._enums_)
        if field.bool:
            return 1 if attr else 0
        if field.enum and isinstance(attr, field.enum):
            return attr.value
        return attr

    def _stable_bytes(self) -> bytes:
        """ Return a stable bytes representation of a struct. """
        buffer = bytearray()
        layout = self._layout_ or self._generate_layout()

        for field in layout:
            if not isinstance(field, Field):
                raise TypeError(f"Expected Field, got {type(field)}")

            attr = getattr(self, field.name)
            attr = self._normalize_out(attr, field)

            T = field.type
            if issubclass(T, PrimitiveType):
                b = T.to_bytes(attr)
                buffer.extend(b)
            elif issubclass(T, BitfieldType):
                b = attr.to_bytes(self._bools_, self._enums_)
                buffer.extend(b)
            elif issubclass(T, (UnionType, ArrayType, StructType)):
                b = attr.to_bytes()
                buffer.extend(b)
            elif issubclass(T, PointerType):
                b = struct.pack('>I', 0x00000000)
                buffer.extend(b)
            else:
                raise TypeError(f"Unsupported field type: {T}")

        return bytes(buffer)

    def get_hash(self):
        """ Return a stable SHA-256 hash as an integer. """
        return int(hashlib.sha256(self._stable_bytes()).hexdigest(), 16)

    def __repr__(self):
        lines = [f'{type(self).__name__}(']

        for name, _ in self._fields_:
            attr = getattr(self, name)
            repr_ = (
                repr(attr)
                if not isinstance(attr, Z64Struct)
                else repr(attr).replace('\n', '\n  ')
            )

            lines.append(f'  {name}={repr_}')
        lines.append(')')

        return '\n'.join(lines)