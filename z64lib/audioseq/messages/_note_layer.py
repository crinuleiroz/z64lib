from z64lib.audioseq.messages import (
    NoteLayerMessage,
    ArgType,
    ArgMessage,
    ArgbitMessage,
    PortamentoMessage,
)
from z64lib.core.enums import AseqVersion


#region Non-Argbits
class AseqLayer_Delay(NoteLayerMessage, ArgMessage):
    """"""
    opcode = 0xC0
    arg_spec = [ArgType.var]


class AseqLayer_ShortVelocity(NoteLayerMessage, ArgMessage):
    opcode = 0xC1
    arg_spec = [ArgType.u8]


class AseqLayer_Transpose(NoteLayerMessage, ArgMessage):
    opcode = 0xC2
    arg_spec = [ArgType.s8]


class AseqLayer_ShortDelay(NoteLayerMessage, ArgMessage):
    opcode = 0xC3
    arg_spec = [ArgType.var]


class AseqLayer_Legato(NoteLayerMessage, ArgMessage):
    opcode = 0xC4


class AseqLayer_Staccato(NoteLayerMessage, ArgMessage):
    opcode = 0xC5


class AseqLayer_Instrument(NoteLayerMessage, ArgMessage):
    opcode = 0xC6
    arg_spec = [ArgType.u8]


class AseqLayer_Portamento(NoteLayerMessage, PortamentoMessage):
    opcode = 0xC7


class AseqLayer_NoPortamento(NoteLayerMessage, ArgMessage):
    opcode = 0xC8


class AseqLayer_ShortGate(NoteLayerMessage, ArgMessage):
    opcode = 0xC9
    arg_spec = [ArgType.u8]


class AseqLayer_NotePan(NoteLayerMessage, ArgMessage):
    opcode = 0xCA
    arg_spec = [ArgType.u8]


class AseqLayer_Envelope(NoteLayerMessage, ArgMessage):
    opcode = 0xCB
    arg_spec = [ArgType.u16, ArgType.u8]


class AseqLayer_NoDrumPan(NoteLayerMessage, ArgMessage):
    opcode = 0xCC


class AseqLayer_Stereo(NoteLayerMessage, ArgMessage):
    opcode = 0xCD
    arg_spec = [ArgType.u8]


class AseqLayer_PitchBend2Semitones(NoteLayerMessage, ArgMessage):
    """ -8192—0—+8191 = -2—0—+2 semitones """
    opcode = 0xCE
    arg_spec = [ArgType.s8]


class AseqLayer_DecayIndex(NoteLayerMessage, ArgMessage):
    opcode = 0xCF
    arg_spec = [ArgType.u8]


class AseqLayer_F0(NoteLayerMessage, ArgMessage):
    opcode = 0xF0
    arg_spec = [ArgType.s16]
    version = AseqVersion.MM


class AseqLayer_SurroundEffect(NoteLayerMessage, ArgMessage):
    opcode = 0xF1
    arg_spec = [ArgType.u8]
    version = AseqVersion.MM
#endregion


#region Argbits
class AseqLayer_LoadShortVel(NoteLayerMessage, ArgbitMessage):
    opcode_range = range(0xD0, 0xE0)
    nbits = 4


class AseqLayer_LoadShortGate(NoteLayerMessage, ArgbitMessage):
    opcode_range = range(0xE0, 0xF0)
    nbits = 4
#endregion


#region Notes
# Legato
class AseqLayer_NoteDVG(NoteLayerMessage, ArgbitMessage):
    is_legato_type = True
    opcode_range = range(0x00, 0x40)
    nbits = 6
    arg_spec = [ArgType.var, ArgType.u8, ArgType.u8]

    @property
    def note(self):
        return self.arg_bits

    @property
    def delay(self):
        return self.args[0].value

    @property
    def velocity(self):
        return self.args[1].value

    @property
    def gate(self):
        return self.args[2].value

    @property
    def midi_note(self):
        return self.arg_bits + 21


class AseqLayer_NoteDV(NoteLayerMessage, ArgbitMessage):
    is_legato_type = True
    opcode_range = range(0x40, 0x80)
    nbits = 6
    arg_spec = [ArgType.var, ArgType.u8]

    @property
    def note(self):
        return self.arg_bits

    @property
    def delay(self):
        return self.args[0].value

    @property
    def velocity(self):
        return self.args[1].value

    @property
    def midi_note(self):
        return self.arg_bits + 21


class AseqLayer_NoteVG(NoteLayerMessage, ArgbitMessage):
    is_legato_type = True
    opcode_range = range(0x80, 0xC0)
    nbits = 6
    arg_spec = [ArgType.u8, ArgType.u8]

    @property
    def note(self):
        return self.arg_bits

    @property
    def velocity(self):
        return self.args[0].value

    @property
    def gate(self):
        return self.args[1].value

    @property
    def midi_note(self):
        return self.arg_bits + 21


# Staccato
class AseqLayer_ShortDVG(NoteLayerMessage, ArgbitMessage):
    is_legato_type = False
    opcode_range = range(0x00, 0x40)
    nbits = 6
    arg_spec = [ArgType.var]

    @property
    def note(self):
        return self.arg_bits

    @property
    def delay(self):
        return self.args[0].value

    @property
    def midi_note(self):
        return self.arg_bits + 21


class AseqLayer_ShortDV(NoteLayerMessage, ArgbitMessage):
    is_legato_type = False
    opcode_range = range(0x40, 0x80)
    nbits = 6
    arg_spec = []

    @property
    def note(self):
        return self.arg_bits

    @property
    def midi_note(self):
        return self.arg_bits + 21


class AseqLayer_ShortVG(NoteLayerMessage, ArgbitMessage):
    is_legato_type = False
    opcode_range = range(0x80, 0xC0)
    nbits = 6
    arg_spec = []

    @property
    def note(self):
        return self.arg_bits

    @property
    def midi_note(self):
        return self.arg_bits + 21
#endregion