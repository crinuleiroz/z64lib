import struct
from z64lib.types.base import DataType
from z64lib.types.markers import BitfieldType


class bitfield(DataType, BitfieldType):
    """ A number of bits that represent a single field in a struct. """
    _FMT_MAP = {
        1: ('>B', '>b'),
        2: ('>H', '>h'),
        4: ('>I', '>i'),
    }
    data_type: type = None
    fields: list[tuple[str, int]] = None

    def __class_getitem__(cls, params):
        """"""
        if not isinstance(params, tuple):
            data_type = params
            fields = None
        else:
            if len(params) != 2:
                raise TypeError()

            data_type, fields = params

            if fields is not None and not isinstance(fields, list):
                raise TypeError()

        return type(
            f'bitfield_{data_type.__name__}',
            (cls,),
            {
                'data_type': data_type,
                'fields': fields,
            },
        )

    def __init__(self, **values):
        self.__dict__.update(values)

    @property
    def signed(self):
        return getattr(self.data_type, 'signed', False)

    @classmethod
    def size(cls):
        return cls.data_type.size()

    @classmethod
    def _is_signed(cls) -> bool:
        return getattr(cls.data_type, 'signed', False)

    @classmethod
    def _fmt(cls) -> str:
        return cls._FMT_MAP[cls.size()][1 if cls._is_signed() else 0]

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int):
        fmt = cls._fmt()
        raw = struct.unpack_from(fmt, buffer, offset)[0]

        bit_cursor = 0
        values = {}

        total_bits = cls.size() * 8
        sum_of_widths = sum(width for _, width in cls.fields)
        if sum_of_widths != total_bits:
            raise ValueError(
                f"Bitfield definition mismatch: sum of field widths ({sum_of_widths}) "
                f"does not equal total size in bits ({total_bits})"
            )

        # Extracts bits from the structure, then performs the relevant
        # separation into a separate attribute for the object.
        for name, width in cls.fields:
            shift = total_bits - bit_cursor - width
            mask = (1 << width) - 1
            value = (raw >> shift) & mask

            if cls._is_signed() and (value & (1 << (width - 1))):
                value -= (1 << width)

            values[name] = value
            bit_cursor += width

        return cls(**values)

    @classmethod
    def to_bytes(self, values: dict):
        fmt = self._fmt()
        bits = 0
        bit_cursor = 0
        total_bits = self.size() * 8

        for name, width in self.fields:
            val = values[name]
            mask = (1 << width) - 1
            shift = total_bits - bit_cursor - width
            bits |= (val & mask) << shift
            bit_cursor += width

        return struct.pack(fmt, bits)

    def __repr__(self):
        field_parts = []
        for name, _bits in self.fields:
            val = getattr(self, name)
            field_parts.append(f'{name}={val}')
        inside = ', '.join(field_parts)
        return f'{type(self).__name__}({inside})'