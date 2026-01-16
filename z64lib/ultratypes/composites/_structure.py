from ..base import *
from typing import ClassVar, Any
from z64lib.core.helpers import bit_helpers


class structure(DataType):
    """
    Composite data type representing a struct.

    #### Attributes
    All attributes are user- or class-defined.

    #### Methods
    `from_bytes()` : class
    `size_of()` : class
    `items()` : instance
    """
    # See z64lib.ultratypes.base
    _data_type: ClassVar[TypeFlag] = TypeFlag.STRUCT
    _alloc_type: ClassVar[TypeFlag] = TypeFlag.STATIC # Can change later

    # structure metadata
    _members_: ClassVar[list[tuple[str, DataType]]] = []
    _attributes_: ClassVar[dict[str, Any]] = dict()
    _bools_: ClassVar[set[str]] = set()
    _enums_: ClassVar[dict[str, type]] = dict()

    # structure internals
    _layout: list[tuple[str, DataType, int, dict]] = None
    _flex_array: tuple[str, DataType] = None
    _align: int = None
    _size: int = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Duplicate parent class attrs to new class
        cls._alloc_type = getattr(cls, '_alloc_type', TypeFlag.STATIC)
        cls._members_ = list(getattr(cls, '_members_', []))
        cls._attributes_ = dict(getattr(cls, '_attributes_', dict()))
        cls._bools_ = set(getattr(cls, '_bools_', set()))
        cls._enums_ = dict(getattr(cls, '_enums_', dict()))

        cls._layout = None
        cls._flex_array = None
        cls._align = None
        cls._size = None

        offset = 0
        layout = []
        struct_align = 1
        flex_array = None

        # User can specify attributes similar to
        # GCC/Clang/MSVC __attribute__((packed)) and #pragma pack(1)
        attributes = cls._attributes_
        attr_pack = attributes.get('pack', None)
        attr_align = attributes.get('align', None)
        attr_size = attributes.get('size', None) # Allow specifying expected size

        if attr_pack in (0,):
            attr_pack = None
        if attr_align in (0, 1):
            attr_align = None

        if not isinstance(cls._members_, list):
            raise TypeError(f"expected list, got {type(cls._members_).__name__}")
        if len(cls._members_) < 1:
            raise ValueError(f"structs require at least 1 member")

        for i, entry in enumerate(cls._members_):
            if len(entry) == 2:
                m_name, m_type = entry
                m_meta = dict()
            elif len(entry) == 3:
                m_name, m_type, m_meta = entry
            else:
                raise TypeError(f"member must be (name, type) or (name, type, meta) tuple")

            if not isinstance(m_name, str):
                raise TypeError(f"expected str, got {type(m_name).__name__}")

            if not (isinstance(m_type, type) and issubclass(m_type, DataType)):
                raise TypeError(f"expected DataType subclass, got {type(m_type).__name__}")

            if not isinstance(m_meta, dict):
                raise TypeError(f"expected dict, got {type(m_meta).__name__}")

            if m_type.is_struct() and m_type.is_dyna():
                if i != len(cls._members_) - 1:
                    raise TypeError(f"nested structs with a flexible array member must be the last struct member")
                if flex_array is not None:
                    raise TypeError(f"structs cannot have multiple flexible array members")
                flex_array = (m_name, m_type)
                continue

            if m_type.is_array() and m_type.is_dyna():
                if flex_array is not None:
                    raise TypeError(f"structs cannot have multiple flexible array members")
                if i != len(cls._members_) - 1:
                    raise TypeError(f"flexible array members must be the last struct member")
                flex_array = (m_name, m_type)
                continue

            t_align = m_type.align_of()
            m_align = m_meta.get('align', None)
            if m_align in (0, 1):
                m_align = None

            # Field alignas()
            if m_align:
                t_align = max(t_align, int(m_align))

            if attr_pack and (attr_pack & (attr_pack - 1)) == 0:
                t_align = min(t_align, attr_pack)

            # Check against a manually set size, otherwise throw an error
            if attr_size and offset > attr_size:
                raise ValueError(f"struct size must be <= {attr_size}")

            aligned_offset = cls.align(offset, t_align)
            layout.append((m_name, m_type, aligned_offset, m_meta))
            offset = aligned_offset + m_type.size_of()

        cls._layout = layout
        cls._flex_array = flex_array

        if attr_align:
            struct_align = attr_align
        else:
            if layout:
                struct_align = 1
                for _, m_type, _, m_meta in layout:
                    t_align = m_type.align_of()
                    m_align = m_meta.get('align', None)
                    if m_align in (0, 1):
                        m_align = None

                    if m_align:
                        t_align = max(t_align, int(m_align))

                    struct_align = max(struct_align, t_align)
            else:
                struct_align = 1

        cls._align = struct_align
        cls._size = cls.align(offset, struct_align)

        if flex_array is not None:
            cls._alloc_type = TypeFlag.DYNAMIC

    # @classmethod
    # def has_flex_array_member(cls) -> bool:
    #     return cls._flex_array is not None

    @classmethod
    def from_bytes(cls, buffer, offset = 0):
        buf = cls._prepare_buffer(buffer, offset, cls.size_of())
        return super(structure, cls).from_bytes(buf, 0)

    @classmethod
    def size_of(cls) -> int:
        if cls._size == 0:
            raise NotImplementedError(f"size_of() is not defined")
        return cls._size

    def items(self):
        cls = type(self)
        for name, *_ in cls._layout or []:
            yield name, getattr(self, name)

    def __getattr__(self, key):
        cls = type(self)

        for name, data_type, member_offset, _ in cls._layout or []:
            if key == name:
                if data_type.is_primitive():
                    ret = data_type(self._buf, self._off + member_offset)
                    if name in cls._bools_:
                        return bool(ret.value)
                    if name in cls._enums_:
                        return cls._enums_[name](ret.value)
                    return ret

                return data_type(self._buf, self._off + member_offset)

            if data_type.is_bitfield() and key in data_type._bit_offsets:
                member = data_type(self._buf, self._off + member_offset)
                start, width = member._bit_offsets[key]
                ret = bit_helpers.extract_bits(
                    member._get_int(),
                    start,
                    width,
                    member._spec_t.num_bits(),
                    member._spec_t.is_signed()
                )
                if key in cls._bools_:
                    ret = bool(ret)
                elif key in cls._enums_:
                    ret = cls._enums_[key](ret)
                return ret

        # TODO: Get flexible array properly implemented
        if cls._flex_array and key == cls._flex_array[0]:
            return None

        raise AttributeError(key)

    def __setattr__(self, key, value):
        cls = type(self)

        for name, data_type, member_offset, _ in cls._layout or []:
            if key == name:
                if data_type.is_primitive():
                    if name in cls._bools_:
                        value = 1 if value else 0
                    if name in cls._enums_:
                        t_enum = cls._enums_[name]
                        if isinstance(value, t_enum):
                            value = value.value
                        elif isinstance(value, int):
                            pass
                        else:
                            raise TypeError(f"expected int or {t_enum.__name__}, got {type(value).__name__}")

                    member = data_type(self._buf, self._off + member_offset)
                    member.value = value
                    return

                elif isinstance(value, DataType):
                    if not isinstance(value, data_type):
                        raise TypeError(f"expected {data_type.__name__}, got {type(value).__name__}")
                    member = data_type(self._buf, self._off + member_offset)
                    member.view[:] = value.view
                    return

                else:
                    raise TypeError(f"expected {data_type.__name__} compatible value, got {type(value).__name__}")

            elif data_type.is_bitfield() and key in data_type._bit_offsets:
                member = data_type(self._buf, self._off + member_offset)
                start, width = member._bit_offsets[key]
                if key in cls._bools_:
                    value = 1 if value else 0
                elif key in cls._enums_:
                    t_enum = cls._enums_[key]
                    if isinstance(value, t_enum):
                        value = value.value
                    elif isinstance(value, int):
                        pass
                    else:
                        raise TypeError(f"expected int or {t_enum.__name__}, got {type(value).__name__}")
                raw = member._get_int()
                new = bit_helpers.insert_bits(
                    raw,
                    value,
                    start,
                    width,
                    member._spec_t.num_bits(),
                    member._spec_t.is_signed(),
                )
                member._set_int(new)
                return

        super().__setattr__(key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __iter__(self):
        cls = type(self)
        for name, *_ in cls._layout or []:
            yield name

    def __contains__(self, key):
        return any(name == key for name, *_ in type(self)._layout or [])

    def __len__(self):
        return len(type(self)._layout or [])

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.buffer == other.buffer

    def __repr__(self):
        cls = type(self)

        parts = []
        for name, data_type, *_ in cls._layout or []:
            member = getattr(self, name)

            if member is None:
                parts.append(f'{name}=None')
                continue

            if data_type.is_primitive():
                if name in cls._bools_:
                    parts.append(f"{name}={bool(member)}")
                elif name in cls._enums_ and isinstance(member, int):
                    parts.append(f"{name}={cls._enums_[name](member).name}")
                else:
                    parts.append(f"{name}={member!r}")

            elif data_type.is_bitfield():
                bf = getattr(self, name)
                bf_parts = []
                for sub_name, (start, width) in data_type._bit_offsets.items():
                    val = getattr(bf, sub_name)
                    if sub_name in cls._bools_:
                        val = bool(val)
                    if sub_name in cls._enums_:
                        val = cls._enums_[sub_name](val)
                    bf_parts.append(f"{sub_name}={val}")

                parts.append(f"{name}=<{type(bf).__name__} {', '.join(p for p in bf_parts)}")

            else:
                parts.append(f"{name}={member!r}")

        if cls._flex_array:
            name, _ = cls._flex_array
            parts.append(f"{name}=<flexible>")

        return f"<{type(self).__name__} {', '.join(parts)}>"