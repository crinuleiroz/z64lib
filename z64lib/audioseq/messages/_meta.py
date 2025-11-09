import struct
from z64lib.audioseq.args import *
from z64lib.audioseq.messages import AseqMessage
from z64lib.core.enums import AseqVersion, AseqSection


class AseqMeta_LoadChannel(AseqMessage):
    opcode_range = range(0x90, 0xA0)
    size = 3
    sections = (AseqSection.META,)
    is_pointer = True

    def __init__(self, channel: int, addr: int):
        self.channel = channel
        self.args = (ArgU16(addr),)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        opcode = data[offset]
        _, arg = struct.unpack_from('>BH', data, offset)
        ch = opcode & 0x0F
        return cls(ch, arg)

    def __repr__(self):
        return f'AseqMeta_LoadChannel(ch={hex(self.channel)}, addr={hex(self.args[0].value)})'