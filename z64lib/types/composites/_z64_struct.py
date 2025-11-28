import hashlib
import struct
from z64lib.types.base import DataType, Field
from z64lib.types.markers import *


class Z64Struct(DataType, StructType):
    """ Static-sized Zelda64 struct. """
    # Type Flags
    is_struct: bool = True

    # Struct specific data
    _fields_: list[tuple[str, DataType]] = []
    _bools_: set[str] = set() # Set of field name
    _enums_: dict[str, type] = dict() # Dictionary of field name and enum class
    _align_: int = 1
    _layout_: list = None
    _struct_size_: int = 0

    # Handlers
    _FROM_BYTES_HANDLERS = {
        'is_primitive': lambda T, buffer, offset, bools, enums: T.from_bytes(buffer, offset),
        'is_bitfield': lambda T, buffer, offset, bools, enums: T.from_bytes(buffer, offset, bools, enums),
        'is_union': lambda T, buffer, offset, bools, enums: T.from_bytes(buffer, offset),
        'is_array': lambda T, buffer, offset, bools, enums: T.from_bytes(buffer, offset),
        'is_struct': lambda T, buffer, offset, bools, enums: T.from_bytes(buffer, offset),
        'is_pointer': lambda T, buffer, offset, bools, enums: T.from_bytes(buffer, offset).dereference(buffer, True),
    }

    _TO_BYTES_HANDLERS = {
        'is_primitive': lambda self, attr, field: field.type.to_bytes(attr),
        'is_bitfield': lambda self, attr, field: attr.to_bytes(self._bools_, self._enums_),
        'is_union': lambda self, attr, field: attr.to_bytes(),
        'is_array': lambda self, attr, field: attr.to_bytes(),
        'is_struct': lambda self, attr, field: attr.to_bytes(),
        'is_pointer': lambda self, attr, field: (
            attr.to_bytes() if isinstance(attr, field.type)
            else field.type(reference=attr).to_bytes() if attr is not None
            else struct.pack('>I', 0x00000000)
        ),
    }

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
    def _describe_field(cls, name, data_type: DataType, offset, attr=None):
        """ Return (Field, new_offset) for one field. """
        offset = data_type.align_field(offset, data_type)

        kind_map = [
            ('is_primitive', 'primitive'),
            ('is_bitfield', 'bitfield'),
            ('is_union', 'union'),
            ('is_array', 'array'),
            ('is_struct', 'struct'),
            ('is_pointer', 'pointer'),
        ]

        kind = None
        for flag, k in kind_map:
            if getattr(data_type, flag, False):
                kind = k
                break
        if kind is None:
            raise TypeError(f"Unsupported type {data_type}")

        if kind == 'array' and data_type.length is None:
            size = (len(attr) * data_type.data_type.size()) if attr else 0
        elif kind == 'struct' and isinstance(attr, Z64Struct):
            size = attr.size()
        else:
            size = data_type.size()

        # T = data_type
        # if T.is_primitive:
        #     size = data_type.size()
        #     kind = 'primitive'
        # elif T.is_bitfield:
        #     size = data_type.size()
        #     kind = 'bitfield'
        # elif T.is_union:
        #     size = data_type.size()
        #     kind = 'union'
        # elif T.is_array:
        #     if data_type.length is None:
        #         size = (len(attr) * data_type.data_type.size()) if attr else 0
        #     else:
        #         size = data_type.size()
        #     kind = 'array'
        # elif T.is_struct:
        #     if isinstance(attr, Z64Struct):
        #         size = attr.size()
        #     else:
        #         size = data_type.size()
        #     kind = 'struct'
        # elif T.is_pointer:
        #     size = data_type.size()
        #     kind = 'pointer'
        # else:
        #     raise TypeError()

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


            T: DataType = field.type
            field_offset = offset + field.offset
            attr = None

            for flag, handler in cls._FROM_BYTES_HANDLERS.items():
                if getattr(T, flag, False):
                    attr = handler(T, buffer, field_offset, cls._bools_, cls._enums_)
                    break
            else:
                raise TypeError(f"Unsupported field type {T}")

            # if T.is_primitive:
            #     attr = T.from_bytes(buffer, field_offset)
            # elif T.is_bitfield:
            #     attr = T.from_bytes(buffer, field_offset, cls._bools_, cls._enums_)
            # elif T.is_union:
            #     attr = T.from_bytes(buffer, field_offset)
            # elif T.is_array:
            #     if T.length is None:
            #         raise TypeError(f"Dynamic array '{field.name}' requires manual length")
            #     attr = T.from_bytes(buffer, field_offset)
            # elif T.is_struct:
            #     attr = T.from_bytes(buffer, field_offset)
            # elif T.is_pointer:
            #     attr = T.from_bytes(buffer, field_offset).dereference(buffer, True)
            # else:
            #     raise TypeError(f"Unsupported field type: {T}")

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

            T: DataType = field.type
            for flag, handler in self._TO_BYTES_HANDLERS.items():
                if getattr(T, flag, False):
                    b = handler(self, attr, field)
                    break
            else:
                raise TypeError(f"Unsupported field type {T}")

            # T: DataType = field.type
            # if T.is_primitive:
            #     b = T.to_bytes(attr)
            # elif T.is_bitfield:
            #     b = attr.to_bytes(self._bools_, self._enums_)
            # elif T.is_union or T.is_array or T.is_struct:
            #     b = attr.to_bytes()
            # elif T.is_pointer:
            #     if attr is None:
            #         b = struct.pack('>I', 0x00000000)
            #     elif isinstance(attr, T):
            #         b = attr.to_bytes()
            #     else:
            #         b = T(reference=attr).to_bytes()
            # else:
            #     raise TypeError(f"Unsupported field type: {T}")

            buffer[field.offset:field.offset + len(b)] = b

        return bytes(buffer)

    @classmethod
    def _normalize_in(cls, attr, field: Field):
        """"""
        if field.type.is_bitfield:
            return attr.normalize_in(cls._bools_, cls._enums_)
        if field.bool:
            return bool(attr)
        if field.enum and not isinstance(attr, field.enum):
            return field.enum(attr)
        return attr

    @classmethod
    def _normalize_out(cls, attr, field: Field):
        """"""
        if field.type.is_bitfield:
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

            T: DataType = field.type
            if T.is_pointer and isinstance(attr, Z64Struct):
                b = attr._stable_bytes()
            else:
                for flag, handler in self._TO_BYTES_HANDLERS.items():
                    if getattr(T, flag, False):
                        b = handler(self, attr, field)
                        break
                else:
                    raise TypeError(f"Unsupported field type {T}")

            buffer.extend(b)

            # T: DataType = field.type
            # if T.is_primitive:
            #     b = T.to_bytes(attr)
            #     buffer.extend(b)
            # elif T.is_bitfield:
            #     b = attr.to_bytes(self._bools_, self._enums_)
            #     buffer.extend(b)
            # elif T.is_union or T.is_array or T.is_struct:
            #     b = attr.to_bytes()
            #     buffer.extend(b)
            # elif T.is_pointer:
            #     if isinstance(attr, Z64Struct):
            #         b = attr._stable_bytes()
            #     else:
            #         b = struct.pack('>I', 0x00000000)
            #     buffer.extend(b)
            # else:
            #     raise TypeError(f"Unsupported field type: {T}")

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