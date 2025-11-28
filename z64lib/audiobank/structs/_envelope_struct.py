import hashlib
from z64lib.core.audio import EnvelopePoint
from z64lib.types import *


class Envelope(DynaStruct):
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
    _fields_ = [
        ('points', array[EnvelopePoint])
    ]
    _align_ = 0x10

    def __init__(self, points=None):
        self.points = points

    @classmethod
    def from_bytes(cls, buffer: bytes, offset: int = 0):
        """"""
        points = []
        cur_offset = offset

        # Loop through the array and create EnvelopePoint objects for each point
        # in the array until it hits an opcode. The game handles the array similarly.
        while True:
            point = EnvelopePoint.from_bytes(buffer, cur_offset)
            points.append(point)
            cur_offset += EnvelopePoint.size()

            if point.is_opcode:
                break

        array_ = array[EnvelopePoint](points)
        return cls(array_)

    def __repr__(self):
        if not self.points:
            return f"{type(self).__name__}([])"
        points_repr = ',\n '.join(repr(p) for p in self.points)
        return f"{type(self).__name__}([\n {points_repr}\n])"