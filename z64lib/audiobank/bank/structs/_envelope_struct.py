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
    _fields_ = []
    _align_ = 0x10

    def __init__(self):
        self.points: list[EnvelopePoint] = []

    def size(self) -> int:
        size = len(self.points) * EnvelopePoint.size_class()
        return (size + (self._align_ - 1) & ~(self._align_ - 1))

    @classmethod
    def from_bytes(cls, buffer: bytes, struct_addr: int = 0):
        obj = cls()
        addr = struct_addr

        # Loop through the array and create EnvelopePoint objects for each point
        # in the array until it hits an opcode. The game handles the array similarly.
        while True:
            point = EnvelopePoint.from_bytes(buffer, addr)
            obj.points.append(point)
            addr += EnvelopePoint.size_class()

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

    def get_hash(self):
        return int(hashlib.sha256(self._stable_bytes()).hexdigest(), 16)

    def _stable_bytes(self) -> bytes:
        data = bytearray()
        for point in self.points:
            data.extend(point.to_bytes())
        return bytes(data)

    def __repr__(self):
        if not self.points:
            return f'{type(self).__name__}([])'
        points_repr = ',\n '.join(repr(p) for p in self.points)
        return f'{type(self).__name__}([\n {points_repr}\n])'