from z64lib.audioseq.messages import (
    AseqLayerMessage, NoArgsMessage, ArgU8Message, ArgS8Message,
    ArgU16Message, ArgS16Message, ArgU16_U8_Message, ArgVarMessage,
    PortamentoMessage
)
from z64lib.core.enums import AseqVersion


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


class AseqLayer_NoDrumPan(AseqLayerMessage, NoArgsMessage):
    opcode = 0xCC


class AseqLayer_Stereo(AseqLayerMessage, ArgU8Message):
    opcode = 0xCD


class AseqLayer_PitchBend2Semitones(AseqLayerMessage, ArgS8Message):
    """ -8192—0—+8191 = -2—0—+2 semitones """
    opcode = 0xCE


class AseqLayer_DecayIndex(AseqLayerMessage, ArgU8Message):
    opcode = 0xCF


class AseqLayer_F0(AseqLayerMessage, ArgS16Message):
    opcode = 0xF0
    version = AseqVersion.MM


class AseqLayer_SurroundEffect(AseqLayerMessage, ArgU8Message):
    opcode = 0xF1
    version = AseqVersion.MM
#endregion


#region Argbits
# class AseqLayer_LoadShortVel(AseqLayerMessage):
#     opcode_range = range(0xD0, 0xE0)


# class AseqLayer_LoadShortGate(AseqLayerMessage):
#     opcode_range = range(0xE0, 0xF0)
#endregion


#region Notes
# Legato
# class AseqLayer_NoteDVG(AseqLayerMessage):
#     opcode_range = range(0x00, 0x40)


# class AseqLayer_NoteDV(AseqLayerMessage):
#     opcode_range = range(0x40, 0x80)


# class AseqLayer_NoteVG(AseqLayerMessage):
#     opcode_range = range(0x80, 0xC0)


# Staccato
# class AseqLayer_ShortDVG(AseqLayerMessage):
#     opcode_range = range(0x00, 0x40)


# class AseqLayer_ShortDV(AseqLayerMessage):
#     opcode_range = range(0x40, 0x80)


# class AseqLayer_ShortVG(AseqLayerMessage):
#     opcode_range = range(0x80, 0xC0)
#endregion