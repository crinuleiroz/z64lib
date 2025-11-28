import inspect
import struct


class DataType:
    """ Base class all struct types inherit their properties from. """
    format: str = None
    signed: bool = False
    _struct: struct.Struct = None

    # Bit Width and Min/Max
    BITS: int = None
    MIN: int = None
    MAX: int = None

    # Type flags
    is_primitive: bool = False
    is_bitfield: bool = False
    is_union: bool = False
    is_array: bool = False
    is_struct: bool = False
    is_pointer: bool = False

    # Static/Dynamic Flags
    is_static: bool = True
    is_dyna: bool = False

    @classmethod
    def size(cls) -> int:
        """ Returns the size of the data type in bytes. """
        if cls.BITS is None:
            raise NotImplementedError
        return (cls.BITS + 7) // 8

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        """"""
        if len(buffer) - offset < cls.size():
            raise ValueError(f"Buffer too small for {cls.__name__}: need {cls.size()} bytes, got {len(buffer) - offset}")

        if issubclass(cls, int):
            data = int.from_bytes(buffer[offset:offset + cls.size()], 'big', signed=cls.signed)
        elif issubclass(cls, float):
            s = cls._get_struct()
            if s is None:
                raise TypeError(f"Cannot parse float type {cls.__name__} without a struct format")
            data = s.unpack_from(buffer, offset)[0]
        else:
            raise TypeError(f"Cannot parse unknown type {cls.__name__}")

        return cls(data)

    @classmethod
    def to_bytes(cls, value) -> bytes:
        """"""
        if value < cls.MIN or value > cls.MAX:
            raise OverflowError(f"Value {value} out of range for {cls.__name__} [{cls.MIN}, {cls.MAX}]")

        # Standard types
        s = cls._get_struct()
        if s is not None:
            if issubclass(cls, int):
                return s.pack(int(value))
            if issubclass(cls, float):
                return s.pack(float(value))
            raise TypeError(f"Unsupported type {cls.__name__}")

        # Non-standard types
        return int(value).to_bytes(cls.size(), 'big', signed=cls.signed)

    @classmethod
    def _wrap(cls, value: int) -> int:
        """ Wrap the value to fit the bit width of the given data type. """
        bitmask = value & (1 << cls.BITS) - 1
        if cls.signed and bitmask >= (1 << (cls.BITS - 1)):
            bitmask -= (1 << cls.BITS)
        return bitmask

    @classmethod
    def _get_struct(cls) -> struct.Struct | None:
        """"""
        if cls.format is None:
            return None
        if cls._struct is None:
            cls._struct = struct.Struct(cls.format)
        return cls._struct

    #region Alignment Helpers
    @staticmethod
    def align_to(value: int, alignment: int) -> int:
        """
        Align the given value to the next multiple of `alignment`.

        Parameters
        ----------
        value: int
            The memory address to align.
        alignment: int
            The alignment boundary (must be a power of two for bitwise correctness).

        Returns
        ----------
        int
            The smallest multiple of `alignment` that is greater than or equal to `value`.

        Notes
        ----------
        The implementation uses `(alignment - 1)` to efficiently round up to the next
        alignment boundary. For example:

        >>> align_to(0x23, 0x10)

        This aligns an address of 0x23 (35) to the next 16-byte (0x10) boundary.
        """
        if alignment == 0:
            return value
        return (value + (alignment - 1)) & ~(alignment - 1)

    @classmethod
    def natural_alignment(cls, data_type) -> int:
        """ Returns the natural alignment for a field type. """
        if hasattr(data_type, 'data_type'):
            return cls.natural_alignment(data_type.data_type)

        if inspect.isclass(data_type) and hasattr(data_type, '_fields_'):
            return max((cls.natural_alignment(f[1]) for f in data_type._fields_), default=1)

        return data_type.size()

    @classmethod
    def align_field(cls, offset: int, data_type) -> int:
        """ Return the offset aligned for this field type. """
        return cls.align_to(offset, cls.natural_alignment(data_type))
    #endregion


class Field:
    __slots__ = (
        'name',
        'type',
        'offset',
        'size',
        'kind',
        'enum',
        'bool',
    )

    def __init__(self, name, type, offset, size, kind, enum, bool):
        self.name = name
        self.type = type
        self.offset = offset
        self.size = size
        self.kind = kind
        self.enum = enum
        self.bool = bool