from ..base import *
from typing import ClassVar


class array(DataType):
    """
    Composite data type representing an array.

    #### Properties
    `view` : memoryview

    #### Methods
    `size_of()` : class
    `get_num_entries()` : instance
    `set_num_entries()` : instance
    `get_size()` : instance
    `to_list()` : instance
    """
    # See z64lib.ultratypes.base
    _data_type: ClassVar[TypeFlag] = TypeFlag.ARRAY
    _alloc_type: ClassVar[TypeFlag] = TypeFlag.STATIC # Can change later

    # array metadata
    _t_elem: ClassVar[DataType | None] = None
    _number_of_entries : ClassVar[int] = 0

    def __class_getitem__(cls, params):
        # If params is not a tuple, then it should
        # be considered a Flexible Array Member
        if not isinstance(params, tuple):
            t_elem = params
            length = 0
            alloc_type = TypeFlag.DYNAMIC
        else:
            if len(params) != 2:
                raise TypeError(f"number of params must be 2")

            t_elem, length = params
            if not issubclass(t_elem, DataType):
                raise TypeError(f"expected DataType subclass, got {type(t_elem).__name__}")
            if not isinstance(length, int):
                raise TypeError(f"expected int, got {type(length).__name__}")
            if length < 0:
                raise ValueError(f"length must be >= 0")

            # Like C, if the array is 0 length
            # treat it as a Flexible Array Member
            alloc_type = TypeFlag.STATIC if length > 0 else TypeFlag.DYNAMIC

        namespace = {
            '_t_elem': t_elem,
            '_number_of_entries': length,
            '_alloc_type': alloc_type,
        }

        return type(f"{cls.__name__}_{t_elem.__name__}_{length}", (cls,), namespace)

    @classmethod
    def size_of(cls):
        elem_size = cls._t_elem.size_of()
        return elem_size * cls._number_of_entries

    def get_num_entries(self) -> tuple[DataType, int, int]:
        cls = type(self)
        elem_t = cls._t_elem
        elem_size = elem_t.size_of()

        if cls.is_static():
            return elem_t, elem_size, cls._number_of_entries
        elif cls.is_dyna() and cls._number_of_entries > 0:
            return elem_t, elem_size, cls._number_of_entries
        else:
            remaining = len(self._buf) - self._off
            return elem_t, elem_size, remaining // elem_size

    def set_num_entries(self, num_entries: int):
        cls = type(self)

        if cls.is_static():
            raise ValueError(f"cannot modify number of entries for static array")
        if num_entries < 0:
            raise ValueError(f"num_entries must be >= 0")

        cls._number_of_entries = num_entries

    def get_size(self):
        _, elem_size, n = self.get_num_entries()
        return elem_size * n

    def to_list(self):
        return [self[i] for i in range(len(self))]

    @property
    def view(self) -> memoryview:
        cls = type(self)
        if cls.is_dyna():
            return self._buf[self._off:self._off + self.get_size()]
        else:
            return self._buf[self._off:self._off + cls.size_of()]

    def __getitem__(self, index):
        elem_t, elem_size, n = self.get_num_entries()

        if not (0 <= index < n):
            raise IndexError(f"index out of range: {index}")

        return elem_t(self._buf, self._off + index * elem_size)

    def __setitem__(self, index, value):
        elem_t, elem_size, n = self.get_num_entries()

        if not (0 <= index < n):
            raise IndexError(f"index out of range: {index}")

        start = self._off + index * elem_size
        end = start + elem_size

        if elem_t.is_primitive():
            if isinstance(value, elem_t):
                src = value.view
            elif elem_t.is_int() and isinstance(value, int):
                tmp = elem_t()
                tmp.value = value
                src = tmp.view
            elif elem_t.is_float() and isinstance(value, float):
                tmp = elem_t()
                tmp.value = value
                src = tmp.view
            else:
                raise TypeError(f"expected {elem_t.__name__} compatible value, got {type(value).__name__}")
        else:
            if not isinstance(value, elem_t):
                raise TypeError(f"expected {elem_t.__name__}, got {type(value).__name__}")

            src = value.view

        self._buf[start:end] = src

    def __contains__(self, item):
        return any(elem == item for elem in self)

    def __iter__(self):
        elem_t, elem_size, n = self.get_num_entries()

        for i in range(n):
            off = self._off + i * elem_size
            yield elem_t(self._buf, off)

    def __len__(self):
        _, _, n = self.get_num_entries()
        return n