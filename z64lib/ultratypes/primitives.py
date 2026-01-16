"""
### z64lib.ultratypes.primitives
"""
from .base import *
from typing import ClassVar
from struct import Struct
from z64lib.core.helpers import bit_helpers


#region Primitive
class primitive(DataType):
    """
    Base class for primtive data types.

    #### Properties
    `value` : int

    #### Methods
    `is_int()` : class
    `is_float()` : class
    `is_signed()` : class
    `is_unsigned()` : class
    `num_bits()` : class
    `min_val()` : class
    `max_val()` : class
    `size_of()` : class
    `from_int()` : class
    `from_float()` : class
    `from_number()` : class
    """
    # See z64lib.ultratypes.base
    _data_t: ClassVar[TypeFlag] = TypeFlag.PRIMITIVE
    _alloc_t: ClassVar[TypeFlag] = TypeFlag.STATIC

    # primitive metadata
    _num_t: ClassVar[TypeFlag | None] = None
    _sign_t: ClassVar[TypeFlag | None] = None
    _bit_width: ClassVar[int | None] = None
    _min_value: ClassVar[int | None] = None
    _max_value: ClassVar[int | None] = None
    _format: ClassVar[str | None] = None
    _struct: ClassVar[Struct | None] = None

    @classmethod
    def is_int(cls) -> bool:
        """ Returns whether the object is a fixed-point data type. """
        if cls._num_t is None:
            raise NotImplementedError(f"_num_t is not defined")
        return cls._num_t == TypeFlag.INTEGER
    @classmethod
    def is_float(cls) -> bool:
        """ Returns whether the object is a floating-point data type. """
        if cls._num_t is None:
            raise NotImplementedError(f"_num_t is not defined")
        return cls._num_t == TypeFlag.FLOAT
    @classmethod
    def is_signed(cls) -> bool:
        """ Returns whether the object's data type is signed. """
        if cls._sign_t is None:
            raise NotImplementedError(f"_sign_t is not defined")
        return cls._sign_t == TypeFlag.SIGNED
    @classmethod
    def is_unsigned(cls) -> bool:
        """ Returns whether the object's data type is unsigned. """
        if cls._sign_t is None:
            raise NotImplementedError(f"_sign_t is not defined")
        return cls._sign_t == TypeFlag.UNSIGNED
    @classmethod
    def num_bits(cls) -> int:
        """ Returns the number of bits the object's data type contains. """
        if cls._bit_width is None:
            raise NotImplementedError(f"_bit_width is not defined")
        return cls._bit_width
    @classmethod
    def min_val(cls) -> int:
        """ Returns the object's data type's minimum allowed value. """
        if cls._min_value is None:
            raise NotImplementedError(f"_min_value is not defined")
        return cls._min_value
    @classmethod
    def max_val(cls) -> int:
        """ Returns the object's data type's maximum allowed value. """
        if cls._bit_width is None:
            raise NotImplementedError(f"_max_value is not defined")
        return cls._max_value

    # Integer overflow is undefined behavior in C
    # and the compiler/user decides how to handle
    # this bahavior. For Python, it is convenient
    # to force an integer to overflow as opposed
    # to throwing an error
    @classmethod
    def _integer_overflow(cls, value: int) -> int:
        """"""
        mask = bit_helpers.mask_lsb(cls.num_bits())
        sign = bit_helpers.mask_msb(cls.num_bits())
        ret = value & mask
        return (ret ^ sign) - sign if cls.is_signed() else ret

    @classmethod
    def _from_numeric_type(cls, value: int | float, expected: type):
        """"""
        if expected is int and not cls.is_int():
            raise TypeError(f"not an integer type")
        if expected is float and not cls.is_float():
            raise TypeError(f"not a float type")
        obj = cls(memoryview(bytearray(cls.size_of())), 0)
        obj.value = value
        return obj

    @classmethod
    def size_of(cls) -> int:
        """"""
        # Non-standard types take advantage of floor division
        # by adding 7 to the number of bits a primitive has
        # For example: 24 + 7 // 8 = |_3.875_| = 3
        return (cls.num_bits() + 7) // 8

    @classmethod
    def from_int(cls, value: int):
        """"""
        return cls._from_numeric_type(value, expected=int)

    @classmethod
    def from_float(cls, value: float):
        """"""
        return cls._from_numeric_type(value, expected=float)

    @classmethod
    def from_number(cls, value: int | float):
        """"""
        if isinstance(value, int):
            expected = int
        elif isinstance(value, float):
            expected = float
        else:
            raise TypeError(f"expected int or float, got {type(value).__name__}")
        return cls._from_numeric_type(value, expected=expected)

    def _coerce_other(self, other):
        """"""
        if isinstance(other, primitive):
            return other.value
        if isinstance(other, (int, float)):
            return other
        raise TypeError(f"unsupported operand type(s): '{type(self).__name__}' and '{type(other).__name__}'")

    @property
    def value(self):
        cls = type(self)
        if not cls.is_primitive():
            raise TypeError(f"not a primtive type")
        if cls.is_int():
            if cls._struct:
                return cls._struct.unpack_from(self._buf, self._off)[0]
            # For non-standard types with no format string,
            # force use of int.from_bytes()
            return int.from_bytes(self.view, 'big', signed=cls.is_signed())
        if cls.is_float():
            if cls._struct:
                return cls._struct.unpack_from(self._buf, self._off)[0]
            raise TypeError("float type requires a struct format")
        raise NotImplementedError

    @value.setter
    def value(self, new):
        cls = type(self)
        if cls.is_int():
            if not isinstance(new, int):
                raise TypeError(f"expected int, got {type(new).__name__}")
            new = cls._integer_overflow(new)
            if cls._struct:
                cls._struct.pack_into(self._buf, self._off, new)
            else:
                # For non-standard types with no format string,
                # force use of int.to_bytes()
                self.view[:] = new.to_bytes(cls.size_of(), 'big', signed=cls.is_signed())
        elif cls.is_float():
            if not isinstance(new, (float, int)):
                raise TypeError(f"expected float, got {type(new).__name__}")
            if cls._struct:
                cls._struct.pack_into(self._buf, self._off, float(new))
            else:
                raise TypeError("float type requires a struct format")
        else:
            raise TypeError(f"cannot assign {type(new).__name__} to {cls.__name__}")

    def __int__(self):
        return self.value

    def __index__(self):
        return int(self.value)

    def __float__(self):
        return self.value

    def __bool__(self):
        return bool(self.value)

    def __hex__(self):
        cls = type(self)
        if cls.is_int():
            int_val = self.value
        elif cls.is_float():
            if cls._struct is None:
                raise TypeError("float type requires a struct format")
            b = bytearray(cls.size_of())
            cls._struct.pack_into(b, 0, self.value)
            int_val = int.from_bytes(b, 'big')
        else:
            raise TypeError(f"cannot convert {cls.__name__} to hex")

        # Take advantage as floor division for non-standard types
        num_nibbles = (cls.num_bits() + 3) // 4
        return f"0x{int_val:0{num_nibbles}x}"

    def __bin__(self):
        cls = type(self)
        if cls.is_int():
            int_val = self.value
        elif cls.is_float():
            if cls._struct is None:
                raise TypeError("float type requries a struct format")
            b = bytearray(cls.size_of())
            cls._struct.pack_into(b, 0, self.value)
            int_val = int.from_bytes(b, 'big')
        else:
            raise TypeError(f"cannot convert {cls.__name__} to bin")

        return f"0b{int_val:0{cls.num_bits()}b}"

    #region Math Dunders
    def __add__(self, other):
        return type(self).from_number(self.value + self._coerce_other(other))

    def __sub__(self, other):
        return type(self).from_number(self.value - self._coerce_other(other))

    def __mul__(self, other):
        return type(self).from_number(self.value * self._coerce_other(other))

    def __truediv__(self, other):
        return type(self).from_number(self.value / self._coerce_other(other))

    def __floordiv__(self, other):
        return type(self).from_number(self.value // self._coerce_other(other))

    def __mod__(self, other):
        return type(self).from_number(self.value % self._coerce_other(other))

    def __and__(self, other):
        return type(self).from_int(self.value & self._coerce_other(other))

    def __or__(self, other):
        return type(self).from_int(self.value | self._coerce_other(other))

    def __xor__(self, other):
        return type(self).from_int(self.value ^ self._coerce_other(other))

    def __lshift__(self, other):
        return type(self).from_int(self.value << self._coerce_other(other))

    def __rshift__(self, other):
        return type(self).from_int(self.value >> self._coerce_other(other))

    def __iadd__(self, other):
        self.value = self.value + self._coerce_other(other)
        return self

    def __isub__(self, other):
        self.value = self.value - self._coerce_other(other)
        return self

    def __imul__(self, other):
        self.value = self.value * self._coerce_other(other)
        return self

    def __itruediv__(self, other):
        self.value = self.value / self._coerce_other(other)
        return self

    def __ifloordiv__(self, other):
        self.value = self.value // self._coerce_other(other)
        return self

    def __imod__(self, other):
        self.value = self.value % self._coerce_other(other)
        return self

    def __iand__(self, other):
        self.value = self.value & self._coerce_other(other)
        return self

    def __ior__(self, other):
        self.value = self.value | self._coerce_other(other)
        return self

    def __ixor__(self, other):
        self.value = self.value ^ self._coerce_other(other)
        return self

    def __ilshift__(self, other):
        self.value = self.value << self._coerce_other(other)
        return self

    def __irshift__(self, other):
        self.value = self.value >> self._coerce_other(other)
        return self

    def __eq__(self, other):
        if not isinstance(other, primitive):
            return NotImplemented
        return self.value == other.value

    def __ne__(self, other):
        if not isinstance(other, primitive):
            return NotImplemented
        return self.value != other.value

    def __lt__(self, other):
        if not isinstance(other, primitive):
            return NotImplemented
        return self.value < other.value

    def __le__(self, other):
        if not isinstance(other, primitive):
            return NotImplemented
        return self.value <= other.value

    def __gt__(self, other):
        if not isinstance(other, primitive):
            return NotImplemented
        return self.value > other.value

    def __ge__(self, other):
        if not isinstance(other, primitive):
            return NotImplemented
        return self.value >= other.value

    def __neg__(self):
        cls = type(self)
        val = -self.value

        if cls.is_int():
            val = cls._integer_overflow(val)

        return cls.from_number(val)

    def __pos__(self):
        return type(self).from_number(self.value)

    def __invert__(self):
        cls = type(self)

        if cls.is_float():
            raise TypeError(f"bad operand type for unary ~: '{cls.__name__}'")

        val = ~self.value
        val = cls._integer_overflow(val)

        return cls.from_number(val)

    def __abs__(self):
        cls = type(self)
        val = abs(self.value)

        if cls.is_int():
            val = cls._integer_overflow(val)

        return cls.from_number(val)

    def __round__(self, ndigits: int = 0):
        cls = type(self)

        val = self.value
        if cls.is_int():
            return int(val)

        elif cls.is_float():
            rounded_val = round(val, ndigits)
            if ndigits == 0:
                return int(rounded_val)
            return rounded_val

        else:
            raise TypeError(f"type {cls.__name__} does not define __round__()")

    def __trunc__(self):
        return int(self.value)

    def __floor__(self):
        import math
        return math.floor(self.value)

    def __ceil__(self):
        import math
        return math.ceil(self.value)

    def __divmod__(self, other):
        cls = type(self)

        if not isinstance(other, primitive):
            raise TypeError(f"unsupported operand type(s) for divmod(): '{type(self).__name__}' and '{type(other).__name__}'")

        a = self.value
        b = other.value

        if b == 0:
            raise ZeroDivisionError("division by zero")

        q = int(a / b)
        r = a - q * b

        q = cls._integer_overflow(q)
        r = cls._integer_overflow(r)

        return (
            cls.from_number(q),
            cls.from_number(r)
        )
    #endregion

    def __repr__(self):
        return f"<{type(self).__name__} {self.value}>"
#endregion


#region 8-Bit
class s8(primitive):
    """ Primitive data type representing a signed 8-bit integer. """
    _num_t: ClassVar[TypeFlag] = TypeFlag.INTEGER
    _sign_t: ClassVar[TypeFlag] = TypeFlag.SIGNED
    _bit_width: ClassVar[int] = 8
    _min_value: ClassVar[int] = -0b10000000
    _max_value: ClassVar[int] = 0b01111111
    _format: ClassVar[str] = '>b'
    _struct: ClassVar[Struct] = Struct('>b')


class u8(primitive):
    """ Primitive data type representing an unsigned 8-bit integer. """
    _num_t: ClassVar[TypeFlag] = TypeFlag.INTEGER
    _sign_t: ClassVar[TypeFlag] = TypeFlag.UNSIGNED
    _bit_width: ClassVar[int] = 8
    _min_value: ClassVar[int] = 0b00000000
    _max_value: ClassVar[int] = 0b11111111
    _format: ClassVar[str] = '>B'
    _struct: ClassVar[Struct] = Struct('>B')
#endregion


#region 16-bit
class s16(primitive):
    """ Primitive data type representing a signed 16-bit integer. """
    _num_t: ClassVar[TypeFlag] = TypeFlag.INTEGER
    _sign_t: ClassVar[TypeFlag] = TypeFlag.SIGNED
    _bit_width: ClassVar[int] = 16
    _min_value: ClassVar[int] = -0b1000000000000000
    _max_value: ClassVar[int] = 0b0111111111111111
    _format: ClassVar[str] = '>h'
    _struct: ClassVar[Struct] = Struct('>h')


class u16(primitive):
    """ Primitive data type representing an unsigned 16-bit integer. """
    _num_t: ClassVar[TypeFlag] = TypeFlag.INTEGER
    _sign_t: ClassVar[TypeFlag] = TypeFlag.UNSIGNED
    _bit_width: ClassVar[int] = 16
    _min_value: ClassVar[int] = 0b0000000000000000
    _max_value: ClassVar[int] = 0b1111111111111111
    _format: ClassVar[str] = '>H'
    _struct: ClassVar[Struct] = Struct('>H')
#endregion


#region 32-bit
class s32(primitive):
    """ Primitive data type representing a signed 32-bit integer. """
    _num_t: ClassVar[TypeFlag] = TypeFlag.INTEGER
    _sign_t: ClassVar[TypeFlag] = TypeFlag.SIGNED
    _bit_width: ClassVar[int] = 32
    _min_value: ClassVar[int] = -0b10000000000000000000000000000000
    _max_value: ClassVar[int] = 0b01111111111111111111111111111111
    _format: ClassVar[str] = '>i'
    _struct: ClassVar[Struct] = Struct('>i')


class u32(primitive):
    """ Primitive data type representing an unsigned 32-bit integer. """
    _num_t: ClassVar[TypeFlag] = TypeFlag.INTEGER
    _sign_t: ClassVar[TypeFlag] = TypeFlag.UNSIGNED
    _bit_width: ClassVar[int] = 32
    _min_value: ClassVar[int] = 0b00000000000000000000000000000000
    _max_value: ClassVar[int] = 0b11111111111111111111111111111111
    _format: ClassVar[str] = '>I'
    _struct: ClassVar[Struct] = Struct('>I')
#endregion


#region 64-bit
class s64(primitive):
    """ Primitive data type representing a signed 64-bit integer. """
    _num_t: ClassVar[TypeFlag] = TypeFlag.INTEGER
    _sign_t: ClassVar[TypeFlag] = TypeFlag.SIGNED
    _bit_width: ClassVar[int] = 64
    _min_value: ClassVar[int] = -0b1000000000000000000000000000000000000000000000000000000000000000
    _max_value: ClassVar[int] = 0b0111111111111111111111111111111111111111111111111111111111111111
    _format: ClassVar[str] = '>q'
    _struct: ClassVar[Struct] = Struct('>q')


class u64(primitive):
    """ Primitive data type representing an unsigned 64-bit integer. """
    _num_t: ClassVar[TypeFlag] = TypeFlag.INTEGER
    _sign_t: ClassVar[TypeFlag] = TypeFlag.UNSIGNED
    _bit_width: ClassVar[int] = 64
    _min_value: ClassVar[int] = 0b0000000000000000000000000000000000000000000000000000000000000000
    _max_value: ClassVar[int] = 0b1111111111111111111111111111111111111111111111111111111111111111
    _format: ClassVar[str] = '>Q'
    _struct: ClassVar[Struct] = Struct('>Q')
#endregion


#region Floating-point
class f32(primitive):
    """ Primitive data type representing a 32-bit single-precision floating-point value. """
    _num_t: ClassVar[TypeFlag] = TypeFlag.FLOAT
    _sign_t: ClassVar[TypeFlag] = TypeFlag.SIGNED
    _bit_width: ClassVar[int] = 32
    _min_value: ClassVar[int] = -3.4028235e38
    _max_value: ClassVar[int] = 3.4028235e38
    _format: ClassVar[str] = '>f'
    _struct: ClassVar[Struct] = Struct('>f')


class f64(primitive):
    """ Primitive data type representing a 64-bit double-precision floating-point value. """
    _num_t: ClassVar[TypeFlag] = TypeFlag.FLOAT
    _sign_t: ClassVar[TypeFlag] = TypeFlag.SIGNED
    _bit_width: ClassVar[int] = 64
    _min_value: ClassVar[int] = -1.7976931348623157e308
    _max_value: ClassVar[int] = 1.7976931348623157e308
    _format: ClassVar[str] = '>d'
    _struct: ClassVar[Struct] = Struct('>d')
#endregion


#region 24-bit
class s24(primitive):
    """ Primitive data type representing a signed 24-bit integer. """
    _num_t: ClassVar[TypeFlag] = TypeFlag.INTEGER
    _sign_t: ClassVar[TypeFlag] = TypeFlag.SIGNED
    _bit_width: ClassVar[int] = 24
    _min_value: ClassVar[int] = -0b100000000000000000000000
    _max_value: ClassVar[int] = 0b011111111111111111111111
    # Non-standard types have no struct format string
    _format: ClassVar[None] = None
    _struct: ClassVar[None] = None


class u24(primitive):
    """ Primitive data type representing an unsigned 24-bit integer. """
    _num_t: ClassVar[TypeFlag] = TypeFlag.INTEGER
    _sign_t: ClassVar[TypeFlag] = TypeFlag.UNSIGNED
    _bit_width: ClassVar[int] = 24
    _min_value: ClassVar[int] = 0b000000000000000000000000
    _max_value: ClassVar[int] = 0b111111111111111111111111
    # Non-standard types have no struct format string
    _format: ClassVar[None] = None
    _struct: ClassVar[None] = None
#endregion


#region Star Imports
__all__ = [
    # Base Type
    'primitive',
    # 8-bit
    's8', 'u8',
    # 16-bit
    's16', 'u16',
    # 32-bit
    's32', 'u32',
    # 64-bit
    's64', 'u64',
    # Floating-point
    'f32', 'f64',
    # 24-bit
    's24', 'u24',
]
#endregion