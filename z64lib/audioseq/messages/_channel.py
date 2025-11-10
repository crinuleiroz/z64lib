from z64lib.audioseq.args import *
from z64lib.audioseq.messages import (
    ChanMessage,
    NoArgsMessage,
    ArgU8Message,
    ArgS8Message,
    ArgU8ArgU8Message,
    ArgU8ArgU16Message,
    ArgS8ArgU16Message,
    ArgU8ArgS16Message,
    ArgS8ArgS16Message,
    ArgU16Message,
    ArgS16Message,
    ArgU16ArgU8Message,
    ArgS16ArgU8Message,
    ArgVarMessage,
    PortamentoMessage
)
from z64lib.core.enums import AseqVersion, AseqSection


#region Non-Argbits
#endregion


#region Argbits
class AseqChannel_LoadLayer(ChanMessage):
    opcode_range = range(0x88, 0x90) # 8 Note Layers?
    size = 3
    is_pointer = True

    def __init__(self, note_layer: int, addr: int):
        self.note_layer = note_layer
        self.args = (ArgU16(addr),)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        ly = cls.read_bits(data, offset, 3)
        arg = cls.read_u16(data, offset)
        return cls(ly, arg)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}(ly={self.note_layer + 1}, arg_u16=0x{self.args[0].value:X})'
#endregion