from z64lib.core.types import *
from z64lib.core.helpers import safe_enum

from z64lib.audio.enums import AdsrOpcode


class EnvelopePoint(Z64Struct):
    """
    Represents a entry in the envelope array, which can be either a time and amplitude pair
    or an opcode and index pair.

    .. code-block:: c

        typedef struct EnvelopePoint {
            /* 0x00 */ s16 timeOrOpcode;
            /* 0x02 */ s16 ampOrIndex;
        } EnvelopePoint; // Size = 0x04

    Attributes
    ----------
    time_or_opcode: int | AdsrOpcode
        If positive, represents time.
        If zero or negative, represents an ADSR opcode (see `AdsrOpcode`).
    amp_or_index: int
        If `time_or_opcode` is time, this value represents the amplitude change
        for the current point.
        If `time_or_opcode` is an opcode, this value represents the index of
        another point in the envelope array.
    is_opcode: bool
        True if `time_or_opcode` represents an opcode; False if it represents a time value.
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
    Represents an envelope, which is an array of `EnvelopePoint` structs.

    The envelope defines amplitude changes over time for an instrument's note.
    Points are read sequentially from memory until and opcode is encountered or
    the note ends.

    In MIPS, words *cannot* begin at an odd memory alignment, they must be 2-byte aligned.

    Attributes
    ----------
    points: list[EnvelopePoint]
        A list of `EnvelopePoint` structs.
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
            offset += EnvelopePoint.size_class()

            if point.is_opcode:
                break

        return obj

    def to_bytes(self) -> bytes:
        data = bytearray()

        for point in self.points:
            data += point.to_bytes()

        aligned_size = (len(data) + self._align_ - 1) & ~(self._align_ - 1)
        data += bytes(aligned_size - len(data))
        return bytes(data)

    def __repr__(self):
        if not self.points:
            return f'{type(self).__name__}([])'
        points_repr = ',\n '.join(repr(p) for p in self.points)
        return f'{type(self).__name__}([\n {points_repr}\n])'