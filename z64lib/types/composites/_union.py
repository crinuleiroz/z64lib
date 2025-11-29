from z64lib.types.base import DataType
from z64lib.types.markers import *


class union(DataType, UnionType):
    """ A struct member whose memory is shared by multiple values. """
    # Type Flags
    is_union: bool = True

    # Union specific data
    max_size: int = None
    fields: list[tuple[str, DataType]] = None

    def __class_getitem__(cls, params):
        if not isinstance(params, tuple) or len(params) != 2:
            raise TypeError()

        max_size, fields = params

        if not isinstance(max_size, int):
            raise TypeError()
        if not isinstance(fields, list):
            raise TypeError()

        return type(
            f'union_{max_size}',
            (cls,),
            {
                'max_size': max_size,
                'fields': fields,
            },
        )

    def __init__(self, **attrs):
        self._attrs = {}

        for name, _data_type in self.fields:
            if name in attrs:
                self._attrs[name] = attrs[name]
            else:
                self._attrs[name] = None

        self._active = next(iter(self._attrs))

    def __getattr__(self, name):
        if name in self._attrs:
            return self._attrs[name]
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in ('_values', '_active', 'fields'):
            return super().__setattr__(name, value)

        if name in self._attrs:
            self._attrs[name] = value
            self._active = name
        else:
            raise AttributeError(f"Invalid union field '{name}'")

    @classmethod
    def size(cls):
        """"""
        if cls.max_size is not None:
            return cls.max_size
        return max(data_type.size() for (_, data_type) in cls.fields)

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        """"""
        size = cls.size()
        raw = buffer[offset:offset + size]
        attrs = {}

        for name, data_type in cls.fields:
            attrs[name] = data_type.from_bytes(raw, 0)

        return cls(**attrs)

    def to_bytes(self) -> bytes:
        """"""
        name = self._active
        data_type = dict(self.fields)[name]
        attr = self._attrs[name]

        buffer = data_type.to_bytes(attr)
        size = type(self).size()

        if len(buffer) < size:
            return buffer + b'\x00' * (size - len(buffer))
        elif len(buffer) > size:
            return buffer[:size]
        return buffer

    @property
    def active_field(self) -> str:
        return self._active

    def set_active(self, name: str):
        """"""
        if name not in self._attrs:
            raise ValueError()
        self._active = name

    def __repr__(self):
        cls_name = type(self).__name__
        parts = []

        for name in self._attrs:
            v = self._attrs[name]
            if name == self._active:
                parts.append(f"{name}={v!r} (active)")
            else:
                parts.append(f"{name}={v!r}")

        inside = ', '.join(parts)
        return f"{cls_name}({inside})"