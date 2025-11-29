import hashlib
import warnings
from z64lib.types.base import DataType, Field, FROM_BYTES_HANDLERS, TO_BYTES_HANDLERS
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
    _size_: int = 0

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

        computed_size = offset
        if cls._align_ > 1:
            computed_size = cls.align_to(offset, cls._align_)

        cls._layout_ = layout
        if cls._size_ > 0:
            if cls._size_ < computed_size:
                warnings.warn(
                    f"{cls.__name__}: manually set _size_ ({cls._size_}) "
                    f"does not match computed size ({computed_size})"
                )
            elif cls._size_ > computed_size:
                warnings.warn(
                    f"{cls.__name__}: manually set _size_ ({cls._size_}) "
                    f"does not match computed size ({computed_size})"
                )
        else:
            cls._size_ = computed_size

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

        enum_cls = cls._enums_.get(name)
        is_bool = name in cls._bools_
        field = Field(name, data_type, offset, size, kind, enum_cls, is_bool)

        return field, offset + size

    @classmethod
    def size(cls) -> int:
        """ Returns the total size of the structure in bytes. """
        return cls._size_

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int = 0, deref_ptrs: bool = True):
        """"""
        obj = cls.__new__(cls)
        layout = cls._layout_ or obj._generate_layout()

        for field in layout:
            if not isinstance(field, Field):
                raise TypeError(f"Expected Field, got {type(field)}")

            T: DataType = field.type
            field_offset = offset + field.offset
            attr = FROM_BYTES_HANDLERS[field.kind](
                T,
                buffer,
                field_offset,
                cls._bools_,
                cls._enums_,
                deref_ptrs=deref_ptrs,
            )

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
            b = TO_BYTES_HANDLERS[field.kind](self, attr, field)
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

            if field.kind == 'pointer' and isinstance(attr, Z64Struct):
                b = attr._stable_bytes()
            else:
                b = TO_BYTES_HANDLERS[field.kind](self, attr, field)

            buffer.extend(b)

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