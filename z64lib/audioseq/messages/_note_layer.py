import struct
from z64lib.audioseq.messages import (
    AseqLayerMessage, NoArgsMessage, ArgU8Message, ArgS8Message,
    ArgU16Message, ArgS16Message, ArgU16_U8_Message, ArgVarMessage,
    PortamentoMessage
)
from z64lib.core.enums import AseqVersion, AseqSection


#region Non-Argbits
class AseqLayer_Delay(AseqLayerMessage, ArgVarMessage):
    """"""
    opcode = 0xC0


class AseqLayer_ShortVelocity(AseqLayerMessage, ArgU8Message):
    opcode = 0xC1


class AseqLayer_Transpose(AseqLayerMessage, ArgS8Message):
    opcode = 0xC2


class AseqLayer_ShortDelay(AseqLayerMessage, ArgVarMessage):
    opcode = 0xC3


class AseqLayer_Legato(AseqLayerMessage, NoArgsMessage):
    opcode = 0xC4


class AseqLayer_Staccato(AseqLayerMessage, NoArgsMessage):
    opcode = 0xC5


class AseqLayer_Instrument(AseqLayerMessage, ArgU8Message):
    opcode = 0xC6


class AseqLayer_Portamento(AseqLayerMessage, PortamentoMessage):
    opcode = 0xC7


class AseqLayer_NoPortamento(AseqLayerMessage, NoArgsMessage):
    opcode = 0xC8


class AseqLayer_ShortGate(AseqLayerMessage, ArgU8Message):
    opcode = 0xC9


class AseqLayer_NotePan(AseqLayerMessage, ArgU8Message):
    opcode = 0xCA

class AseqLayer_Envelope(AseqLayerMessage, ArgU16_U8_Message):
    opcode = 0xCB
#endregion


#region Argbits
#endregion