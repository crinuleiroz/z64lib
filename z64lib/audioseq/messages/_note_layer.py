from z64lib.audioseq.messages import (
    NoteLayerMessage,
    NoArgsMessage,
    ArgU8Message,
    ArgS8Message,
    ArgS16Message,
    ArgU16ArgU8Message,
    ArgVarMessage,
    PortamentoMessage
)
from z64lib.core.enums import AseqVersion


#region Non-Argbits
class AseqLayer_Delay(NoteLayerMessage, ArgVarMessage):
    """"""
    opcode = 0xC0


class AseqLayer_ShortVelocity(NoteLayerMessage, ArgU8Message):
    opcode = 0xC1


class AseqLayer_Transpose(NoteLayerMessage, ArgS8Message):
    opcode = 0xC2


class AseqLayer_ShortDelay(NoteLayerMessage, ArgVarMessage):
    opcode = 0xC3


class AseqLayer_Legato(NoteLayerMessage, NoArgsMessage):
    opcode = 0xC4


class AseqLayer_Staccato(NoteLayerMessage, NoArgsMessage):
    opcode = 0xC5


class AseqLayer_Instrument(NoteLayerMessage, ArgU8Message):
    opcode = 0xC6


class AseqLayer_Portamento(NoteLayerMessage, PortamentoMessage):
    opcode = 0xC7


class AseqLayer_NoPortamento(NoteLayerMessage, NoArgsMessage):
    opcode = 0xC8


class AseqLayer_ShortGate(NoteLayerMessage, ArgU8Message):
    opcode = 0xC9


class AseqLayer_NotePan(NoteLayerMessage, ArgU8Message):
    opcode = 0xCA


class AseqLayer_Envelope(NoteLayerMessage, ArgU16ArgU8Message):
    opcode = 0xCB


class AseqLayer_NoDrumPan(NoteLayerMessage, NoArgsMessage):
    opcode = 0xCC


class AseqLayer_Stereo(NoteLayerMessage, ArgU8Message):
    opcode = 0xCD


class AseqLayer_PitchBend2Semitones(NoteLayerMessage, ArgS8Message):
    """ -8192—0—+8191 = -2—0—+2 semitones """
    opcode = 0xCE


class AseqLayer_DecayIndex(NoteLayerMessage, ArgU8Message):
    opcode = 0xCF


class AseqLayer_F0(NoteLayerMessage, ArgS16Message):
    opcode = 0xF0
    version = AseqVersion.MM


class AseqLayer_SurroundEffect(NoteLayerMessage, ArgU8Message):
    opcode = 0xF1
    version = AseqVersion.MM
#endregion


#region Argbits
# class AseqLayer_LoadShortVel(NoteLayerMessage):
#     opcode_range = range(0xD0, 0xE0)


# class AseqLayer_LoadShortGate(NoteLayerMessage):
#     opcode_range = range(0xE0, 0xF0)
#endregion


#region Notes
# Legato
# class AseqLayer_NoteDVG(NoteLayerMessage):
#     opcode_range = range(0x00, 0x40)


# class AseqLayer_NoteDV(NoteLayerMessage):
#     opcode_range = range(0x40, 0x80)


# class AseqLayer_NoteVG(NoteLayerMessage):
#     opcode_range = range(0x80, 0xC0)


# Staccato
# class AseqLayer_ShortDVG(NoteLayerMessage):
#     opcode_range = range(0x00, 0x40)


# class AseqLayer_ShortDV(NoteLayerMessage):
#     opcode_range = range(0x40, 0x80)


# class AseqLayer_ShortVG(NoteLayerMessage):
#     opcode_range = range(0x80, 0xC0)
#endregion