from z64lib.audioseq.args import *
from z64lib.audioseq.messages import (
    AseqChanMessage, NoArgsMessage, ArgU8Message, ArgS8Message,
    ArgU16Message, ArgS16Message, ArgVarMessage, PortamentoMessage
)
from z64lib.core.enums import AseqVersion, AseqSection


#region Non-Argbits
#endregion


#region Argbits
class AseqChannel_LoadLayer(AseqChanMessage):
    opcode_range = range(0x88, 0x90) # 8 Note Layers?
    size = 3
    is_pointer = True

    def __init__(self, note_layer: int, addr: int):
        self.note_layer = note_layer
        self.args = (ArgU16(addr),)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        opcode = data[offset]
        arg = cls.read_u16(data, offset)
        ly = opcode & 0x07
        return cls(ly, arg)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}(ly={self.note_layer + 1}, arg_u16=0x{self.args[0].value:X})'
#endregion