from z64lib.audioseq.args import *
from z64lib.audioseq.messages import (
    MetaMessage,
    ArgType,
    ArgMessage,
    ArgbitMessage,
)
from z64lib.core.enums import AseqVersion


#region Non-Argbits
class AseqMeta_AllocateVoices(MetaMessage, ArgMessage):
    """"""
    opcode = 0xF1
    arg_spec = [ArgType.u8]


class AseqMeta_FreeVoices(MetaMessage, ArgMessage):
    """"""
    opcode = 0xF0


class AseqMeta_EF(MetaMessage, ArgMessage):
    """"""
    opcode = 0xEF
    arg_spec = [ArgType.s16, ArgType.u8]


class AseqMeta_Transpose(MetaMessage, ArgMessage):
    """"""
    opcode = 0xDF
    arg_spec = [ArgType.s8]


class AseqMeta_TransposeRelative(MetaMessage, ArgMessage):
    """"""
    opcode = 0xDE
    arg_spec = [ArgType.s8]


class AseqMeta_Tempo(MetaMessage, ArgMessage):
    """"""
    opcode = 0xDD
    arg_spec = [ArgType.u8]


class AseqMeta_TempoChange(MetaMessage, ArgMessage):
    """"""
    opcode = 0xDC
    arg_spec = [ArgType.s8]


class AseqMeta_MasterVolume(MetaMessage, ArgMessage):
    """"""
    opcode = 0xDB
    arg_spec = [ArgType.u8]


class AseqMeta_VolumeMode(MetaMessage, ArgMessage):
    """"""
    opcode = 0xDA
    arg_spec = [ArgType.u8, ArgType.s16]


class AseqMeta_MasterExpression(MetaMessage, ArgMessage):
    """"""
    opcode = 0xD9
    arg_spec = [ArgType.u8]


class AseqMeta_InitChannels(MetaMessage, ArgMessage):
    """"""
    opcode = 0xD7
    arg_spec = [ArgType.u16]


class AseqMeta_FreeChannels(MetaMessage, ArgMessage):
    """"""
    opcode = 0xD6
    arg_spec = [ArgType.u16]


class AseqMeta_MuteScale(MetaMessage, ArgMessage):
    """"""
    opcode = 0xD5
    arg_spec = [ArgType.s8]


class AseqMeta_Mute(MetaMessage, ArgMessage):
    """"""
    opcode = 0xD4


class AseqMeta_MuteBehavior(MetaMessage, ArgMessage):
    """"""
    opcode = 0xD3
    arg_spec = [ArgType.u8]


class AseqMeta_LoadShortVelArray(MetaMessage, ArgMessage):
    """"""
    opcode = 0xD2
    arg_spec = [ArgType.u16]


class AseqMeta_LoadShortGateArray(MetaMessage, ArgMessage):
    """"""
    opcode = 0xD1
    arg_spec = [ArgType.u16]


class AseqMeta_VoicePolicy(MetaMessage, ArgMessage):
    """"""
    opcode = 0xD0
    arg_spec = [ArgType.u8]


class AseqMeta_Random(MetaMessage, ArgMessage):
    """"""
    opcode = 0xCE
    arg_spec = [ArgType.u8]


class AseqMeta_DynCall(MetaMessage, ArgMessage):
    """"""
    opcode = 0xCD
    arg_spec = [ArgType.u16]


class AseqMeta_LoadImmediate(MetaMessage, ArgMessage):
    """"""
    opcode = 0xCC
    arg_spec = [ArgType.u8]


class AseqMeta_BitwiseAnd(MetaMessage, ArgMessage):
    """"""
    opcode = 0xC9
    arg_spec = [ArgType.u8]


class AseqMeta_Subtract(MetaMessage, ArgMessage):
    """"""
    opcode = 0xC8
    arg_spec = [ArgType.u8]


class AseqMeta_WriteSequenceScript(MetaMessage, ArgMessage):
    """"""
    opcode = 0xC7
    arg_spec = [ArgType.s8, ArgType.u16]


class AseqMeta_Stop(MetaMessage, ArgMessage):
    """"""
    opcode = 0xC6


class AseqMeta_ScriptCounter(MetaMessage, ArgMessage):
    """"""
    opcode = 0xC5
    arg_spec = [ArgType.u16]


class AseqMeta_RunSequence(MetaMessage, ArgMessage):
    """"""
    opcode = 0xC4
    arg_spec = [ArgType.u8, ArgType.u8]


class AseqMeta_MuteChannel(MetaMessage, ArgMessage):
    """"""
    opcode = 0xC3
    arg_spec = [ArgType.u16]
    version = AseqVersion.MM
#endregion


#region Argbits
class AseqMeta_TestChannel(MetaMessage, ArgbitMessage):
    """"""
    opcode_range = range(0x00, 0x10)
    nbits = 4


class AseqMeta_StopChannel(MetaMessage, ArgbitMessage):
    """"""
    opcode_range = range(0x40, 0x50)
    nbits = 4


class AseqMeta_SubIO(MetaMessage, ArgbitMessage):
    """"""
    opcode_range = range(0x50, 0x58)
    nbits = 3


class AseqMeta_LoadResource(MetaMessage, ArgbitMessage):
    """"""
    opcode_range = range(0x60, 0x70)
    nbits = 4
    arg_spec = [ArgType.u8, ArgType.u8]


class AseqMeta_StoreIO(MetaMessage, ArgbitMessage):
    """"""
    opcode_range = range(0x70, 0x78)
    nbits = 3


class AseqMeta_LoadIO(MetaMessage, ArgbitMessage):
    """"""
    opcode_range = range(0x80, 0x88)
    nbits = 3


class AseqMeta_LoadChannel(MetaMessage, ArgbitMessage):
    """"""
    opcode_range = range(0x90, 0xA0)
    nbits = 4
    arg_spec = [ArgType.u16]
    is_pointer = True

    @property
    def channel(self):
        return self.arg_bits


class AseqMeta_LoadChannelRelative(MetaMessage, ArgbitMessage):
    """"""
    opcode_range = range(0xA0, 0xB0)
    nbits = 4
    arg_spec = [ArgType.s16]
    is_pointer = True


class AseqMeta_LoadSequence(MetaMessage, ArgbitMessage):
    """"""
    opcode_range = range(0xB0, 0xC0)
    nbits = 4
    arg_spec = [ArgType.u8, ArgType.u16]
    is_pointer = True
#endregion