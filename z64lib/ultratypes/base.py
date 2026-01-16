"""
### z64lib.ultratypes.base
"""
from enum import IntEnum
from typing import ClassVar


class TypeFlag(IntEnum):
    # Numeric Flags
    INTEGER = 1 << 0
    FLOAT = 1 << 1

    # Sign Type Flags
    UNSIGNED = 1 << 2
    SIGNED = 1 << 3

    # Data Type Flags
    PRIMITIVE = 1 << 4
    BITFIELD = 1 << 5
    UNION = 1 << 6
    ARRAY = 1 << 7
    STRUCT = 1 << 8
    POINTER = 1 << 9

    # Allocation Type Flags
    STATIC = 1 << 10
    DYNAMIC = 1 << 11

    @classmethod
    def combine(cls, *flags) -> int:
        """"""
        ret = 0
        for flag in flags:
            ret |= flag
        return ret

    @classmethod
    def has_flag(cls, value, flag) -> bool:
        """"""
        return (value & flag) != 0


#region DataType
class DataType:
    """
    Base class representing all data types.

    #### Properties
    `view` : memoryview
    `buffer` : bytes

    #### Methods
    `is_primitive()` : class
    `is_bitfield()` : class
    `is_union()` : class
    `is_array()` : class
    `is_struct()` : class
    `is_pointer()` : class
    `is_composite()` : class
    `is_reference()` : class
    `is_static()` : class
    `is_dyna()` : class
    `from_bytes()` : class
    `size_of()` : class
    `to_bytes()` : instance
    `cast_to()` : instance
    `align()` : static
    `insert_padding()` : static
    """
    # The '_data_t' and '_alloc_t' determine
    # what type the class is and if the size is static
    # or is dynamic and depends on runtime variables to
    # be calculated
    _data_t: ClassVar[TypeFlag | None] = None
    _alloc_t: ClassVar[TypeFlag | None] = None

    # _max_align_t : ClassVar[int | None] = None
    _align_as: ClassVar[int | None] = None

    def __init__(self, buffer: bytes | bytearray | memoryview | None = None, offset: int = 0):
        cls = type(self)
        buf = cls._prepare_buffer(buffer, offset, cls.size_of())

        self._buf = buf#cls._ensure_buffer_size(buf, offset)
        self._off = offset

    @classmethod
    def is_primitive(cls) -> bool:
        """ Return whether the object is a primitive data type. """
        if cls._data_t is None:
            raise NotImplementedError(f"_data_t is not defined")
        return cls._data_t == TypeFlag.PRIMITIVE
    @classmethod
    def is_bitfield(cls) -> bool:
        """ Return whether the object is a bitfield data type. """
        if cls._data_t is None:
            raise NotImplementedError(f"_data_t is not defined")
        return cls._data_t == TypeFlag.BITFIELD
    @classmethod
    def is_union(cls) -> bool:
        """ Return whether the object is a union data type. """
        if cls._data_t is None:
            raise NotImplementedError(f"_data_t is not defined")
        return cls._data_t == TypeFlag.UNION
    @classmethod
    def is_array(cls) -> bool:
        """ Return whether the object is an array data type. """
        if cls._data_t is None:
            raise NotImplementedError(f"_data_t is not defined")
        return cls._data_t == TypeFlag.ARRAY
    @classmethod
    def is_struct(cls) -> bool:
        """ Return whether the object is a struct data type. """
        if cls._data_t is None:
            raise NotImplementedError(f"_data_t is not defined")
        return cls._data_t == TypeFlag.STRUCT
    @classmethod
    def is_pointer(cls) -> bool:
        """ Return whether the object is a pointer data type. """
        if cls._data_t is None:
            raise NotImplementedError(f"_data_t is not defined")
        return cls._data_t == TypeFlag.POINTER
    @classmethod
    def is_composite(cls) -> bool:
        """ Return whether the object is a composite (bitfield, union, array, struct) data type. """
        if cls._data_t is None:
            raise NotImplementedError(f"_data_t is not defined")
        composite = TypeFlag.combine(TypeFlag.BITFIELD, TypeFlag.UNION, TypeFlag.ARRAY, TypeFlag.STRUCT)
        return TypeFlag.has_flag(cls._data_t, composite)
    @classmethod
    def is_reference(cls) -> bool:
        """ Return whether the object is a reference (pointer) data type. """
        if cls._data_t is None:
            raise NotImplementedError(f"_data_t is not defined")
        reference = TypeFlag.combine(TypeFlag.POINTER)
        return TypeFlag.has_flag(reference)
    @classmethod
    def is_static(cls) -> bool:
        """ Return whether the object has a static memory layout. """
        if cls._alloc_t is None:
            raise NotImplementedError(f"_data_t is not defined")
        return cls._alloc_t == TypeFlag.STATIC
    @classmethod
    def is_dyna(cls) -> bool:
        """ Return whether the object has a dynamic memory layout. """
        if cls._alloc_t is None:
            raise NotImplementedError(f"_data_t is not defined")
        return cls._alloc_t == TypeFlag.DYNAMIC

    @classmethod
    def align_of(cls) -> int:
        if cls._align_as is not None:
            return cls._align_as

        if cls.is_struct():
            return cls._align

        return cls.size_of()

    @classmethod
    def align_as(cls, other: int | type['DataType']):
        if isinstance(other, int):
            if other <= 0:
                raise ValueError("other must be > 0")
            cls._align_as = other
        else:
            cls._align_as = other.align_of()

    @classmethod
    def _prepare_buffer(cls, buffer: bytes | bytearray | memoryview | None, offset: int, total_size: int):
        """"""
        if buffer is None:
            buf = memoryview(bytearray(total_size))
        elif isinstance(buffer, bytes):
            buf = memoryview(bytearray(buffer))
        elif isinstance(buffer, bytearray):
            buf = memoryview(buffer)
        else:
            if not isinstance(buffer, memoryview):
                raise TypeError(f"buffer must be a bytes-like, not {type(buffer).__name__}")
            buf = buffer

        return buf

    @classmethod
    def _ensure_buffer_size(cls, buffer: memoryview, offset: int = 0) -> memoryview:
        """"""
        expected = cls.size_of()
        actual = len(buffer) - offset
        if offset < 0:
            raise ValueError(f"offset must be >= 0")
        if actual < expected:
            raise ValueError(f"buffer is too small: need {expected} bytes, have {actual}")
        return buffer

    @classmethod
    def from_bytes(cls, buffer: bytes | bytearray | memoryview, offset: int = 0):
        """"""
        if not isinstance(buffer, (bytes, bytearray, memoryview)):
            raise TypeError(f"argument must be a bytes-like object, not {type(buffer).__name__}")

        if isinstance(buffer, memoryview):
            buf = buffer.obj if isinstance(buffer.obj, bytearray) else bytearray(buffer)
        else:
            buf = bytearray(buffer)

        return cls(buf, offset)

    @classmethod
    def size_of(cls) -> int:
        """"""
        raise NotImplementedError(f"size_of() is not implemented")

    def to_bytes(self) -> bytes:
        """"""
        # TODO: Add handling for dynamic structs
        return self.buffer

    def cast_to(self, target_cls: type['DataType']) -> 'DataType':
        tgt_size = target_cls.size_of()
        avail = len(self._buf) - self._off

        if avail < tgt_size:
            raise ValueError(f"cannot cast: need {tgt_size} bytes, have {avail}")
        return target_cls(self._buf, self._off)

    @property
    def view(self) -> memoryview:
        """"""
        return self._buf[self._off:self._off+self.size_of()]

    @property
    def buffer(self) -> bytes:
        """"""
        return self.view.tobytes()

    @staticmethod
    def align(value: int, alignment: int = 0x10) -> int:
        """"""
        if alignment == 0:
            return value
        return (value + alignment - 1) & ~(alignment - 1)

    @staticmethod
    def insert_padding(buffer: bytes | bytearray | memoryview, insert_at: int, pad_len: int):
        """"""
        if not isinstance(buffer, (bytes, bytearray, memoryview)):
            raise TypeError(f"buffer must be a bytes-like, not {type(buffer).__name__}")

        if pad_len < 0:
            raise ValueError("pad length must be >= 0")
        if pad_len == 0:
            return buffer

        if not isinstance(buffer, memoryview):
            buffer = memoryview(buffer)

        orig = buffer
        orig_len = len(buffer)
        new_len = orig_len + pad_len

        new_buf = bytearray(new_len)
        new_buf[:insert_at] = orig[:insert_at]
        new_buf[insert_at + pad_len:] = orig[insert_at:]

        # Do not return a sliced buffer
        return memoryview(new_buf)

    def __bytes__(self):
        return self.buffer

    def __repr__(self):
        return f"<{type(self).__name__} {self.view}>"
#endregion


#region Star Imports
__all__ = [
    # Enums
    'TypeFlag',
    # Base type
    'DataType',
]
#endregion