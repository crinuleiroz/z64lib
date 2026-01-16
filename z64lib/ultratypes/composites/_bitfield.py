from ..base import *
from typing import ClassVar
from z64lib.core.helpers import bit_helpers


class bitfield(DataType):
    """
    Composite data type representing a bitfield.

    #### Attributes
    All attributes are user- or class-defined.

    #### Methods
    `size_of()` : class
    """
    # See z64lib.ultratypes.base
    _data_t: ClassVar[TypeFlag] = TypeFlag.BITFIELD
    _alloc_t: ClassVar[TypeFlag] = TypeFlag.STATIC

    # bitfield metadata
    _spec_t: ClassVar[DataType | None] = None
    _member_defs: ClassVar[list[tuple[str, int]] | None] = None
    _bit_offsets: ClassVar[dict[str, tuple[int, int]] | None] = None

    def __class_getitem__(cls, params):
        if not isinstance(params, tuple):
            raise TypeError(f"expected tuple, got {type(params).__name__}")
        if len(params) != 2:
            raise ValueError(f"number of params must be 2")

        spec_t, members = params
        if not (isinstance(spec_t, type) and issubclass(spec_t, DataType)):
            raise TypeError(f"expected DataType subclass, got {type(spec_t).__name__}")

        if not (spec_t.is_primitive() and spec_t.is_int()):
            raise TypeError(f"expected integer primitive type, got {type(spec_t).__name__}")

        if members is not None and not isinstance(members, list):
            raise TypeError(f"expected list, got {type(members).__name__}")

        bit_offsets = {}
        pos = 0
        for name, width in members:
            if not isinstance(name, str):
                raise TypeError(f"expected str, got {type(name).__name__}")
            if not name.strip():
                raise ValueError(f"member name cannot be empty")

            if not isinstance(width, int):
                raise TypeError(f"expected int, got {type(width).__name__}")
            if width <= 0:
                raise ValueError(f"bit width must be > 0")

            bit_offsets[name] = (pos, width)
            pos += width

        if pos > spec_t._bit_width:
            raise ValueError(f"total width must be <= {spec_t._bit_width}")

        namespace = {
            '_spec_t': spec_t,
            '_member_defs': members,
            '_bit_offsets': bit_offsets,
        }

        return type(f"bitfield_{spec_t.__name__}", (cls,), namespace)

    @classmethod
    def size_of(cls) -> int:
        return cls._spec_t.size_of()

    def _get_int(self):
        spec_t = type(self)._spec_t
        base = spec_t(self._buf, self._off)
        return base.value

    def _set_int(self, value: int):
        spec_t = type(self)._spec_t
        base = spec_t(self._buf, self._off)
        base.value = value

    def __getattr__(self, key):
        cls = type(self)
        offsets = cls._bit_offsets
        bits = cls._spec_t.num_bits()
        signed = cls._spec_t.is_signed()

        if key not in offsets:
            raise AttributeError(key)

        start, width = offsets[key]
        raw = self._get_int()
        return bit_helpers.extract_bits(raw, start, width, bits, signed)

    def __setattr__(self, key, value):
        cls = type(self)
        offsets = cls._bit_offsets
        bits = cls._spec_t.num_bits()
        signed = cls._spec_t.is_signed()

        if key in offsets:
            if not isinstance(value, int):
                raise TypeError(f"expected int, got {type(value).__name__}")

            start, width = offsets[key]
            raw = self._get_int()
            new = bit_helpers.insert_bits(raw, value, start, width, bits, signed)
            self._set_int(new)
            return

        super().__setattr__(key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __int__(self):
        return self._get_int()

    def __index__(self):
        return int(self)

    def __bool__(self):
        return bool(int(self))

    def __hex__(self):
        return hex(int(self))

    def __bin__(self):
        bits = type(self)._spec_t._BITS
        return format(int(self), f"0{bits}b")

    #region Math Dunders
    def __and__(self, other):
        cls = type(self)
        new_val = int(self) & int(other)
        new_obj = cls(self._buf, self._off)
        new_obj._set_int(new_val)
        return new_obj

    def __or__(self, other):
        cls = type(self)
        new_val = int(self) | int(other)
        new_obj = cls(self._buf, self._off)
        new_obj._set_int(new_val)
        return new_obj

    def __xor__(self, other):
        cls = type(self)
        new_val = int(self) ^ int(other)
        new_obj = cls(self._buf, self._off)
        new_obj._set_int(new_val)
        return new_obj

    def __lshift__(self, other):
        cls = type(self)
        new_val = int(self) << int(other)
        new_obj = cls(self._buf, self._off)
        new_obj._set_int(new_val)
        return new_obj

    def __rshift__(self, other):
        cls = type(self)
        new_val = int(self) >> int(other)
        new_obj = cls(self._buf, self._off)
        new_obj._set_int(new_val)
        return new_obj

    def __iand__(self, other):
        self._set_int(int(self) & int(other))
        return self

    def __ior__(self, other):
        self._set_int(int(self) | int(other))
        return self

    def __ixor__(self, other):
        self._set_int(int(self) ^ int(other))
        return self

    def __ilshift__(self, other):
        self._set_int(int(self) << int(other))
        return self

    def __irshift__(self, other):
        self._set_int(int(self) >> int(other))
        return self

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return int(self) == int(other)
        elif isinstance(other, int):
            return int(self) == other
        return NotImplemented

    def __ne__(self, other):
        eq = self.__eq__(other)
        if eq is NotImplemented:
            return NotImplemented
        return not eq

    def __lt__(self, other):
        if isinstance(other, (type(self), int)):
            return int(self) < int(other)
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, (type(self), int)):
            return int(self) <= int(other)
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, (type(self), int)):
            return int(self) > int(other)
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, (type(self), int)):
            return int(self) >= int(other)
        return NotImplemented

    def __invert__(self):
        spec_bits = type(self)._spec_t._BITS
        mask = bit_helpers.mask_lsb(spec_bits)
        new_val = ~int(self) & mask

        cls = type(self)
        new_obj = cls(self._buf, self._off)
        new_obj._set_int(new_val)
        return new_obj
    #endregion

    def __repr__(self):
        cls = type(self)
        items = []
        for name, (start, width) in cls._bit_offsets.items():
            val = getattr(self, name)
            items.append(f"{name}={val}")
        return f"<{cls.__name__} {', '.join(items)}>"