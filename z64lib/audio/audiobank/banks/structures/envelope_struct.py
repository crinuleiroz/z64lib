from z64lib.core.types import *
from z64lib.core.helpers import safe_enum

from z64lib.audio.audiobank.enums import AdsrOpcode


class EnvelopePoint(Z64Struct):
    """
    Represents a single pair of time or opcode and amp or index values in an envelope array.

    .. code-block:: c

        typedef struct EnvelopePoint {
            /* 0x00 */ s16 timeOrOpcode;
            /* 0x02 */ s16 ampOrIndex;
        } EnvelopePoint; // Size = 0x04
    """
    _fields_ = [
        ('_time_or_opcode', s16),
        ('amp_or_index', s16)
    ]

    @property
    def time_or_opcode(self):
        val = self._time_or_opcode

        if val <= 0:
            return safe_enum(AdsrOpcode, val)
        else:
            return val

    @property
    def is_opcode(self):
        return self._time_or_opcode <= 0

    def __repr__(self):
        return (
            f'{type(self).__name__}('
            f'time_or_opcode={self.time_or_opcode}, '
            f'amp_or_index={self.amp_or_index}'
        )


class Envelope(Z64Struct):
    """
    Represents an array of EnvelopePoint structures in the instrument bank.

    In MIPS, words *cannot* begin at an odd memory alignment, they must be 2-byte aligned.
    """
    _fields_ = []
    _align_ = 0x10

    def __init__(self):
        self.points: list[EnvelopePoint] = []

    @classmethod
    def from_bytes(cls, buffer: bytes, struct_offset: int = 0):
        obj = cls()
        offset = struct_offset

        # Loop through the array and create EnvelopePoint objects for each point
        # in the array until it hits an opcode. The game handles the array similarly.
        while True:
            point = EnvelopePoint.from_bytes(buffer, offset)
            obj.points.append(point)
            offset += EnvelopePoint.size()

            if point.is_opcode:
                break

        return obj

    def __repr__(self):
        if not self.points:
            return f'{type(self).__name__}([])'
        points_repr = ',\n '.join(repr(p) for p in self.points)
        return f'{type(self).__name__}([\n {points_repr}\n])'