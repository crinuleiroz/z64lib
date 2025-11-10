from z64lib.audioseq.args import *
from z64lib.audioseq.messages import (
    AseqMetaMessage, NoArgsMessage, ArgU8Message, ArgS8Message,
    ArgU16Message, ArgS16Message, ArgVarMessage, PortamentoMessage
)
from z64lib.core.enums import AseqVersion, AseqSection


#region Non-Argbits
#endregion


#region Argbits
class AseqMeta_LoadChannel(AseqMetaMessage):
    opcode_range = range(0x90, 0xA0)
    size = 3
    is_pointer = True

    def __init__(self, channel: int, addr: int):
        self.channel = channel
        self.args = (ArgU16(addr),)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        opcode = data[offset]
        arg = cls.read_u16(data, offset)
        ch = opcode & 0x0F
        return cls(ch, arg)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}(ch={self.channel + 1}, arg_u16=0x{self.args[0].value:X})'
#endregion