from z64lib.audioseq.messages import (
    ChanMessage,
    ArgType,
    ArgMessage,
    ArgbitMessage,
)
from z64lib.core.enums import AseqVersion


#region Non-Argbits
class AseqChannel_AllocateVoices(ChanMessage, ArgMessage):
    """"""
    opcode = 0xF1
    arg_spec = [ArgType.u8]


class AseqChannel_FreeVoices(ChanMessage, ArgMessage):
    """"""
    opcode = 0xF0


class AseqChannel_PitchBend2Semitones(ChanMessage, ArgMessage):
    """"""
    opcode = 0xEE
    arg_spec = [ArgType.s8]


class AseqChannel_Gain(ChanMessage, ArgMessage):
    """"""
    opcode = 0xED
    arg_spec = [ArgType.u8]


class AseqChannel_ResetParams(ChanMessage, ArgMessage):
    """"""
    opcode = 0xEC


class AseqChannel_BankInstrument(ChanMessage, ArgMessage):
    """"""
    opcode = 0xEB
    arg_spec = [ArgType.u8, ArgType.u8]


class AseqChannel_Stop(ChanMessage, ArgMessage):
    """"""
    opcode = 0xEA


class AseqChannel_VoicePriority(ChanMessage, ArgMessage):
    """"""
    opcode = 0xE9
    arg_spec = [ArgType.u8]

    @property
    def some_other_priority(self):
        return (self.args[0].value & 0b11110000) >> 4

    @property
    def priority(self):
        return self.args[0].value & 0b00001111


class AseqChannel_Params(ChanMessage, ArgMessage):
    """"""
    opcode = 0xE8
    arg_spec = [ArgType.u8, ArgType.u8, ArgType.u8, ArgType.s8, ArgType.s8, ArgType.u8, ArgType.u8, ArgType.u8]


class AseqChannel_LoadParams(ChanMessage, ArgMessage):
    """"""
    opcode = 0xE7
    arg_spec = [ArgType.u16]
    is_pointer = True


class AseqChannel_SampleCodebook(ChanMessage, ArgMessage):
    """"""
    opcode = 0xE6
    arg_spec = [ArgType.u8]


class AseqChannel_ReverbIndex(ChanMessage, ArgMessage):
    """"""
    opcode = 0xE5
    arg_spec = [ArgType.u8]


class AseqChannel_DynCall(ChanMessage, ArgMessage):
    """"""
    opcode = 0xE4


class AseqChannel_VibratoDelay(ChanMessage, ArgMessage):
    """"""
    opcode = 0xE3
    arg_spec = [ArgType.u8]


class AseqChannel_VibratoDepthEnvelope(ChanMessage, ArgMessage):
    """"""
    opcode = 0xE2
    arg_spec = [ArgType.u8, ArgType.u8, ArgType.u8]


class AseqChannel_VibratoPitchEnvelope(ChanMessage, ArgMessage):
    """"""
    opcode = 0xE1
    arg_spec = [ArgType.u8, ArgType.u8, ArgType.u8]


class AseqChannel_Expression(ChanMessage, ArgMessage):
    """"""
    opcode = 0xE0
    arg_spec = [ArgType.u8]


class AseqChannel_Volume(ChanMessage, ArgMessage):
    """"""
    opcode = 0xDF
    arg_spec = [ArgType.u8]


class AseqChannel_PitchScale(ChanMessage, ArgMessage):
    """"""
    opcode = 0xDE
    arg_spec = [ArgType.u16]


class AseqChannel_Pan(ChanMessage, ArgMessage):
    """"""
    opcode = 0xDD
    arg_spec = [ArgType.u8]


class AseqChannel_PanWeight(ChanMessage, ArgMessage):
    """"""
    opcode = 0xDC
    arg_spec = [ArgType.u8]


class AseqChannel_Transpose(ChanMessage, ArgMessage):
    """"""
    opcode = 0xDB
    arg_spec = [ArgType.s8]


class AseqChannel_Envelope(ChanMessage, ArgMessage):
    """"""
    opcode = 0xDA
    arg_spec = [ArgType.u16]


class AseqChannel_DecayIndex(ChanMessage, ArgMessage):
    """"""
    opcode = 0xD9
    arg_spec = [ArgType.u8]


class AseqChannel_VibratoDepth(ChanMessage, ArgMessage):
    """"""
    opcode = 0xD8
    arg_spec = [ArgType.u8]


class AseqChannel_VibratoPitch(ChanMessage, ArgMessage):
    """"""
    opcode = 0xD7
    arg_spec = [ArgType.u8]


class AseqChannel_ReverbVolume(ChanMessage, ArgMessage):
    """"""
    opcode = 0xD4
    arg_spec = [ArgType.u8]


class AseqChannel_PitchBend12Semitones(ChanMessage, ArgMessage):
    """"""
    opcode = 0xD3
    arg_spec = [ArgType.s8]


class AseqChannel_Sustain(ChanMessage, ArgMessage):
    """"""
    opcode = 0xD2
    arg_spec = [ArgType.u8]


class AseqChannel_VoicePolicy(ChanMessage, ArgMessage):
    """"""
    opcode = 0xD1
    arg_spec = [ArgType.u8]


class AseqChannel_Effects(ChanMessage, ArgMessage):
    """"""
    opcode = 0xD0
    arg_spec = [ArgType.u8]

    @property
    def headset(self):
        return bool((self.args[0].value >> 7) & 1)

    @property
    def type(self):
        return (self.args[0].value >> 4) & 0b00000011

    @property
    def strong_right(self):
        return (self.args[0].value >> 3) & 1

    @property
    def strong_left(self):
        return (self.args[0].value >> 2) & 1

    @property
    def strong_reverb_right(self):
        return (self.args[0].value >> 1) & 1

    @property
    def strong_reverb_left(self):
        return (self.args[0].value >> 0) & 1


class AseqChannel_WritePointerToSequence(ChanMessage, ArgMessage):
    """"""
    opcode = 0xCF
    arg_spec = [ArgType.u16]


class AseqChannel_LoadPointer(ChanMessage, ArgMessage):
    """"""
    opcode = 0xCE
    arg_spec = [ArgType.u16]
    is_pointer = True


class AseqChannel_StopChannel(ChanMessage, ArgMessage):
    """"""
    opcode = 0xCD
    arg_spec = [ArgType.u8]


class AseqChannel_LoadImmediate(ChanMessage, ArgMessage):
    """"""
    opcode = 0xCC
    arg_spec = [ArgType.u8]


class AseqChannel_LoadSequence(ChanMessage, ArgMessage):
    """"""
    opcode = 0xCB
    arg_spec = [ArgType.u16]
    is_pointer = True


class AseqChannel_MuteBehavior(ChanMessage, ArgMessage):
    """"""
    opcode = 0xCA
    arg_spec = [ArgType.u8]


class AseqChannel_BitwiseAnd(ChanMessage, ArgMessage):
    """"""
    opcode = 0xC9
    arg_spec = [ArgType.u8]


class AseqChannel_Subtract(ChanMessage, ArgMessage):
    """"""
    opcode = 0xC8
    arg_spec = [ArgType.u8]


class AseqChannel_WriteSequence(ChanMessage, ArgMessage):
    """"""
    opcode = 0xC7
    arg_spec = [ArgType.u8, ArgType.u16]


class AseqChannel_Bank(ChanMessage, ArgMessage):
    """"""
    opcode = 0xC6
    arg_spec = [ArgType.u8]


class AseqChannel_DynTableLookup(ChanMessage, ArgMessage):
    """"""
    opcode = 0xC5


class AseqChannel_Legato(ChanMessage, ArgMessage):
    """"""
    opcode = 0xC4


class AseqChannel_Staccato(ChanMessage, ArgMessage):
    """"""
    opcode = 0xC3


class AseqChannel_DynTable(ChanMessage, ArgMessage):
    """"""
    opcode = 0xC2
    arg_spec = [ArgType.u16]


class AseqChannel_Instrument(ChanMessage, ArgMessage):
    """"""
    opcode = 0xC1
    arg_spec = [ArgType.u8]


class AseqChannel_BE(ChanMessage, ArgMessage):
    """"""
    opcode = 0xBE
    arg_spec = [ArgType.u8]
    version = AseqVersion.MM


class AseqChannel_RandomPointer_OOT(ChanMessage, ArgMessage):
    """"""
    opcode = 0xBD
    arg_spec = [ArgType.u16, ArgType.u16]
    version = AseqVersion.OOT


class AseqChannel_SampleStart(ChanMessage, ArgMessage):
    """"""
    opcode = 0xBD
    arg_spec = [ArgType.u8]
    version = AseqVersion.MM


class AseqChannel_PointerAdd(ChanMessage, ArgMessage):
    """"""
    opcode = 0xBC
    arg_spec = [ArgType.u16]


class AseqChannel_Chorus(ChanMessage, ArgMessage):
    """"""
    opcode = 0xBB
    arg_spec = [ArgType.u8, ArgType.u16]


class AseqChannel_RandomGateVariance(ChanMessage, ArgMessage):
    """ Bugged """
    opcode = 0xBA
    arg_spec = [ArgType.u8]


class AseqChannel_RandomVelocityVariance(ChanMessage, ArgMessage):
    """"""
    opcode = 0xB9
    arg_spec = [ArgType.u8]


class AseqChannel_Random(ChanMessage, ArgMessage):
    """"""
    opcode = 0xB8
    arg_spec = [ArgType.u8]


class AseqChannel_RandomToPointer(ChanMessage, ArgMessage):
    """"""
    opcode = 0xB7
    arg_spec = [ArgType.u16]


class AseqChannel_DynTableVelocity(ChanMessage, ArgMessage):
    """"""
    opcode = 0xB6


class AseqChannel_DynTableToPointer(ChanMessage, ArgMessage):
    """"""
    opcode = 0xB5


class AseqChannel_PointerToDynTable(ChanMessage, ArgMessage):
    """"""
    opcode = 0xB4


class AseqChannel_Filter(ChanMessage, ArgMessage):
    """"""
    opcode = 0xB3
    arg_spec = [ArgType.u8]


class AseqChannel_LoadSequenceToPointer(ChanMessage, ArgMessage):
    """"""
    opcode = 0xB2
    arg_spec = [ArgType.u16]


class AseqChannel_FreeFilter(ChanMessage, ArgMessage):
    """"""
    opcode = 0xB1


class AseqChannel_LoadFilter(ChanMessage, ArgMessage):
    """"""
    opcode = 0xB0
    arg_spec = [ArgType.u16]
    is_pointer = True


class AseqChannel_RandomPointer_MM(ChanMessage, ArgMessage):
    """"""
    opcode = 0xA8
    arg_spec = [ArgType.u16, ArgType.u16]
    version = AseqVersion.MM


class AseqChannel_A7(ChanMessage, ArgMessage):
    """"""
    opcode = 0xA7
    arg_spec = [ArgType.u8]
    version = AseqVersion.MM


class AseqChannel_A6(ChanMessage, ArgMessage):
    """"""
    opcode = 0xA6
    arg_spec = [ArgType.u8, ArgType.s16]
    version = AseqVersion.MM


class AseqChannel_A5(ChanMessage, ArgMessage):
    """"""
    opcode = 0xA5
    version = AseqVersion.MM


class AseqChannel_A4(ChanMessage, ArgMessage):
    """"""
    opcode = 0xA4
    arg_spec = [ArgType.u8]
    version = AseqVersion.MM


class AseqChannel_A3(ChanMessage, ArgMessage):
    """"""
    opcode = 0xA3
    version = AseqVersion.MM


class AseqChannel_A2(ChanMessage, ArgMessage):
    """"""
    opcode = 0xA2
    arg_spec = [ArgType.s16]
    version = AseqVersion.MM


class AseqChannel_A1(ChanMessage, ArgMessage):
    """"""
    opcode = 0xA1
    version = AseqVersion.MM


class AseqChannel_A0(ChanMessage, ArgMessage):
    """"""
    opcode = 0xA0
    arg_spec = [ArgType.s16]
    version = AseqVersion.MM
#endregion


#region Argbits
class AseqChannel_ChannelDelay(ChanMessage, ArgbitMessage):
    """"""
    opcode_range = range(0x00, 0x10)
    nbits = 4


class AseqChannel_LoadSample(ChanMessage, ArgbitMessage):
    """"""
    opcode_range = range(0x10, 0x18)
    nbits = 3


class AseqChannel_LoadChannel(ChanMessage, ArgbitMessage):
    """"""
    opcode_range = range(0x20, 0x30)
    nbits = 4
    arg_spec = [ArgType.u16]
    is_pointer = True


class AseqChannel_WriteChannelIO(ChanMessage, ArgbitMessage):
    """"""
    opcode_range = range(0x30, 0x40)
    nbits = 4
    arg_spec = [ArgType.u8]


class AseqChannel_LoadChannelIO(ChanMessage, ArgbitMessage):
    """"""
    opcode_range = range(0x40, 0x50)
    nbits = 4
    arg_spec = [ArgType.u8]


class AseqChannel_SubIO(ChanMessage, ArgbitMessage):
    """"""
    opcode_range = range(0x50, 0x58)
    nbits = 3


class AseqChannel_LoadIO(ChanMessage, ArgbitMessage):
    """"""
    opcode_range = range(0x60, 0x68)
    nbits = 3


class AseqChannel_WriteIO(ChanMessage, ArgbitMessage):
    """"""
    opcode_range = range(0x70, 0x78)
    nbits = 3


class AseqChannel_LoadLayerRelative(ChanMessage, ArgbitMessage):
    """"""
    opcode_range = range(0x78, 0x80)
    nbits = 3
    arg_spec = [ArgType.u16]
    is_pointer = True


class AseqChannel_TestLayer(ChanMessage, ArgbitMessage):
    """"""
    opcode_range = range(0x80, 0x88)
    nbits = 3


class AseqChannel_LoadLayer(ChanMessage, ArgbitMessage):
    """"""
    opcode_range = range(0x88, 0x90)
    nbits = 3
    arg_spec = [ArgType.u16]
    is_pointer = True

    @property
    def note_layer(self):
        return self.arg_bits


class AseqChannel_DeleteLayer(ChanMessage, ArgbitMessage):
    """"""
    opcode_range = range(0x90, 0x98)
    nbits = 3


class AseqChannel_DynLoadLayer(ChanMessage, ArgbitMessage):
    """"""
    opcode_range = range(0x98, 0xA0)
    nbits = 3
#endregion