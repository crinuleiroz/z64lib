from ..base import *
from typing import ClassVar


class union(DataType):
    """
    Composite data type representing a union.

    #### Attributes
    All attributes are user- or class-defined.

    #### Properties
    `active` : DataType

    #### Methods
    `size_of()` : class
    """
    # See z64lib.ultratypes.base
    _data_t: ClassVar[TypeFlag] = TypeFlag.UNION
    _alloc_t: ClassVar[TypeFlag] = TypeFlag.STATIC

    # union metadata
    _size: ClassVar[int | None] = None # Number of bytes allocated for union mem
    _members: ClassVar[list[tuple[str, DataType]] | None] = None

    def __class_getitem__(cls, params):
        if not isinstance(params, tuple):
            raise ValueError(f"expected tuple, got {type(params).__name__}")
        if len(params) != 2:
            raise ValueError(f"number of params must be 2")

        size, members = params
        if not isinstance(size, int):
            raise TypeError(f"expected int, got {type(size).__name__}")

        if not isinstance(members, list):
            raise TypeError(f"expected list, got {type(members).__name__}")

        union_members = {}
        for name, data_type in members:
            if not isinstance(name, str):
                raise TypeError(f"expected str, got {type(name).__name__}")
            if not name.strip():
                raise ValueError(f"member name cannot be empty")

            if not issubclass(data_type, DataType):
                raise TypeError(f"expected DataType subclass, got {type(data_type).__name__}")

            if data_type.size_of() > size:
                raise ValueError(f"member size must be <= {size}")

            union_members[name] = data_type

        namespace = {
            '_size': size,
            '_members': members,
        }

        return type(f"union_{size}", (cls,), namespace)

    def __init__(self, buffer=None, offset=0):
        super().__init__(buffer, offset)

        cls = type(self)
        self._active = None

        # C-style default active to first member when initialized
        if cls._members:
            first_name, first_type = cls._members[0]
            self._active = first_name

    @classmethod
    def size_of(cls):
        return cls._size

    @property
    def active(self):
        return self._active

    def __getattr__(self, key):
        cls = type(self)
        for name, data_type in cls._members:
            if name == key:
                return data_type(self._buf, self._off)
        raise AttributeError(key)

    def __setattr__(self, key, value):
        cls = type(self)

        for name, data_type in cls._members:
            if name == key:
                member = data_type(self._buf, self._off)

                if isinstance(value, DataType):
                    if not isinstance(value, data_type):
                        raise TypeError(f"expected {data_type.__name__}, got {type(value).__name__}")

                    member.view[:] = value.buffer
                    super().__setattr__('_active', key)
                    return

                if data_type.is_primitive():
                    member.value = value
                    super().__setattr__('_active', key)
                    return

                raise TypeError(f"expected primitive value or {data_type.__name__}, got {type(value).__name__}")

        super().__setattr__(key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __repr__(self):
        return f"<{type(self).__name__} size={self._size} active={self._active}>"