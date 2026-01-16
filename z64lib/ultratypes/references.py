"""
### z64lib.ultratypes.references
"""
from .base import *
from typing import ClassVar


#region Pointer
class pointer(DataType):
    """
    Reference data type representing a pointer.

    #### Properties
    `address` : int

    #### Methods
    `size_of()` : class
    `dereference()` : instance
    `add()` : instance
    `subtract()` : instance
    `i_add()` : instance
    `i_subtract()` : instancea
    """
    # See z64lib.ultratypes.base
    _data_type: ClassVar[TypeFlag] = TypeFlag.POINTER
    _alloc_type: ClassVar[TypeFlag] = TypeFlag.STATIC

    # pointer metadata
    _t_spec: ClassVar[DataType | None] = None
    _depth: ClassVar[int] = 1

    def __class_getitem__(cls, params):
        if not isinstance(params, tuple):
            t_spec = params
            depth = 1
        elif len(params) != 2:
            t_spec = params
            depth = 1
        else:
            t_spec, depth = params

        if not issubclass(t_spec, DataType):
            raise TypeError()
        if not isinstance(depth, int) or depth < 1:
            raise TypeError()

        namespace = {
            '_t_spec': t_spec,
            '_depth': depth,
        }

        return type(f"pointer_{t_spec.__name__}_d{depth}", (cls,), namespace)

    @classmethod
    def size_of(cls):
        return 4 # Always 4 bytes except audioseq script's 2 byte pointers

    def dereference(self, *, safe_mode: bool = False):
        cls = type(self)
        t_spec = cls._t_spec
        depth = cls._depth

        try:
            self._check_bounds(self.address, t_spec.size_of(), check_32bit=True)
        except IndexError:
            if safe_mode:
                return self.address
            raise

        if depth == 1:
            return t_spec(self._buf, self.address)
        else:
            return pointer[t_spec, depth - 1](self._buf, self.address)

    def add(self, n: int):
        cls = type(self)
        t_spec = cls._t_spec

        new_addr = self.address + n * t_spec.size_of()

        new_buf = bytearray(cls.size_of())
        new_ptr = cls(new_buf, 0)
        new_ptr.address = new_addr
        return new_ptr

    def subtract(self, n: int):
        cls = type(self)
        t_spec = cls._t_spec

        new_addr = self.address - n * t_spec.size_of()

        new_buf = bytearray(cls.size_of())
        new_ptr = cls(new_buf, 0)
        new_ptr.address = new_addr
        return new_ptr

    def i_add(self, n: int):
        self.address += n * type(self)._t_spec.size_of()
        return self

    def i_subtract(self, n: int):
        self.address -= n * type(self)._t_spec.size_of()
        return self

    @property
    def address(self):
        return int.from_bytes(self.view, 'big', signed=False)

    @address.setter
    def address(self, new):
        if not isinstance(new, int):
            raise TypeError(f"expected int, got {type(new).__name__}")

        self._check_bounds(new, type(self).size_of(), check_32bit=True)
        self.view[:] = new.to_bytes(4, 'big', signed=False)

    def _check_bounds(self, offset: int, size: int, *, check_32bit: bool = True):
        if offset < 0:
            raise IndexError(f"offset must be >= 0")
        if size < 0:
            raise ValueError(f"size must be >= 0")
        if offset + size > len(self._buf):
            raise IndexError(f"index out of range: {offset + size}")
        if check_32bit and offset + size > 0xFFFFFFFF:
            raise OverflowError(f"address must be <= 0xFFFFFFFF")

    def __getitem__(self, index: int):
        cls = type(self)
        t_spec = cls._t_spec
        depth = cls._depth

        if not isinstance(index, int):
            raise TypeError(f"expected int, got {type(index).__name__}")

        new_addr = self.address + index * t_spec.size_of()

        try:
            self._check_bounds(new_addr, t_spec.size_of())
        except IndexError:
            # return new_addr
            raise

        if depth == 1:
            return t_spec(self._buf, new_addr)
        else:
            return pointer[t_spec, depth - 1](self._buf, new_addr)

    def __setitem__(self, index: int, value):
        cls = type(self)
        t_spec = cls._t_spec
        depth = cls._depth

        new_addr = self.address + index * t_spec.size_of()
        self._check_bounds(new_addr, t_spec.size_of())

        if depth == 1:
            if not isinstance(value, t_spec):
                raise TypeError(f"expected {t_spec.__name__}, got {type(value).__name__}")
            self._buf[new_addr:new_addr + t_spec.size_of()] = value.view
        else:
            if not isinstance(value, pointer[t_spec, depth - 1]):
                raise TypeError(f"expected pointer_{t_spec.__name__}_d{depth - 1}, got {type(value).__name__}")
            self._buf[new_addr:new_addr + t_spec.size_of()] = value.view

    def __int__(self):
        return self.address

    def __add__(self, n: int): return self.add(n)
    def __sub__(self, n: int): return self.subtract(n)
    def __iadd__(self, n: int): return self.i_add(n)
    def __isub__(self, n: int): return self.i_subtract(n)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.address == other.address
#endregion


#region Star Imports
__all__ = [
    'pointer',
]
#endregion