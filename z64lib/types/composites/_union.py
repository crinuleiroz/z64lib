from z64lib.types.base import DataType
from z64lib.types.markers import *


class union(DataType, UnionType):
    """ A struct member whose memory is shared by multiple values. """
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

    def __init__(self, **values):
        self._values = {}

        for name, data_type in self.fields:
            if name in values:
                self._values[name] = values[name]
            else:
                self._values[name] = None

        self._active = next(iter(self._values))

    def __getattr__(self, name):
        if name in self._values:
            return self._values[name]
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in ('_values', '_active', 'fields'):
            return super().__setattr__(name, value)

        if name in self._values:
            self._values[name] = value
            self._active = name
        else:
            raise AttributeError(f"Invalid union field '{name}'")

    @classmethod
    def size(cls):
        if cls.max_size is not None:
            return cls.max_size
        return max(data_type.size() for (_, data_type) in cls.fields)

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        size = cls.size()
        raw = buffer[offset:offset + size]
        values = {}

        for name, data_type in cls.fields:
            values[name] = data_type.from_bytes(raw, 0)

        return cls(**values)

    def to_bytes(self) -> bytes:
        name = self._active
        data_type = dict(self.fields)[name]
        value = self._values[name]

        raw = data_type.to_bytes(value)
        size = type(self).size()

        if len(raw) < size:
            return raw + b'\x00' * (size - len(raw))
        elif len(raw) > size:
            return raw[:size]
        return raw

    @property
    def active_field(self) -> str:
        return self._active

    def set_active(self, name: str):
        if name not in self._values:
            raise ValueError()
        self._active = name

    def __repr__(self):
        cls_name = type(self).__name__
        parts = []

        for name in self._values:
            v = self._values[name]
            if name == self._active:
                parts.append(f"{name}={v!r} (active)")
            else:
                parts.append(f"{name}={v!r}")

        inside = ", ".join(parts)
        return f"{cls_name}({inside})"