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

    def __init__(self, data_type, bit_width):
        self.data_type = data_type
        self.bit_width = bit_width

    @property
    def signed(self):
        return self.data_type.signed

    def size(self):
        return self.data_type.size()

    def _fmt(self):
        return self._FMT_MAP[self.size()][1 if self.signed else 0]

    def from_bytes(self, buffer: bytes, offset: int, bit_cursor: int):
        format = self._fmt()

        # Extracts bits from the structure, then performs the relevant operations
        # to split the specified bit into a separate attribute for the object.
        bits = struct.unpack_from(format, buffer, offset)[0]
        bit_shift = self.size() * 8 - bit_cursor - self.bit_width
        bit_mask = (1 << self.bit_width) - 1
        bit_value = (bits >> bit_shift) & bit_mask

        # Sign extension
        if self.signed and (bit_value & (1 << (self.bit_width - 1))):
            bit_value -= (1 << self.bit_width)

        return bit_value

    def to_bytes(self, bit_value: int, bit_cursor: int, base_value: int = 0) -> tuple[bytes, int]:
        format = self._fmt()

        # Pack the bits back into a single value.
        bit_shift = self.size() * 8 - bit_cursor - self.bit_width
        bit_mask = (1 << self.bit_width) - 1
        bits = base_value | ((bit_value & bit_mask) << bit_shift)

        return struct.pack(format, bits), bits