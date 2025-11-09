import struct
from z64lib.audioseq.args import *
from z64lib.audioseq.messages import AseqMessage
from z64lib.core.enums import AseqVersion, AseqSection


class AseqChannel_LoadLayer(AseqMessage):
    opcode_range = range(0x88, 0x90) # 8 Note Layers?
    size = 3
    sections = (AseqSection.CHAN,)
    is_pointer = True

    def __init__(self, note_layer: int, addr: int):
        self.note_layer = note_layer
        self.args = (ArgU16(addr),)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        opcode = data[offset]
        _, arg = struct.unpack_from('>BH', data, offset)
        ly = opcode & 0x07
        return cls(ly, arg)

    def __repr__(self):
        return f'AseqChan_LoadLayer(ly={hex(self.note_layer)}, addr={hex(self.args[0].value)})'