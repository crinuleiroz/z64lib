from z64lib.audioseq.args import *
from z64lib.audioseq.messages import (
    MetaMessage,
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
from z64lib.core.enums import AseqVersion


#region Non-Argbits
class AseqMeta_AllocateVoices(MetaMessage, ArgU8Message):
    opcode = 0xF1


class AseqMeta_FreeVoices(MetaMessage, NoArgsMessage):
    opcode = 0xF0


class AseqMeta_EF(MetaMessage, ArgS16ArgU8Message):
    opcode = 0xEF


class AseqMeta_Transpose(MetaMessage, ArgS8Message):
    opcode = 0xDF


class AseqMeta_TransposeRelative(MetaMessage, ArgS8Message):
    opcode = 0xDE


class AseqMeta_Tempo(MetaMessage, ArgU8Message):
    opcode = 0xDD


class AseqMeta_TempoChange(MetaMessage, ArgS8Message):
    opcode = 0xDC


class AseqMeta_MasterVolume(MetaMessage, ArgU8Message):
    opcode = 0xDB


class AseqMeta_VolumeMode(MetaMessage, ArgU8ArgS16Message):
    opcode = 0xDA


class AseqMeta_MasterExpression(MetaMessage, ArgU8Message):
    opcode = 0xD9


class AseqMeta_InitChannels(MetaMessage, ArgU16Message):
    opcode = 0xD7


class AseqMeta_FreeChannels(MetaMessage, ArgU16Message):
    opcode = 0xD6


class AseqMeta_MuteScale(MetaMessage, ArgS8Message):
    opcode = 0xD5


class AseqMeta_Mute(MetaMessage, NoArgsMessage):
    opcode = 0xD4


class AseqMeta_MuteBehavior(MetaMessage, ArgU8Message):
    opcode = 0xD3


class AseqMeta_LoadShortVelArray(MetaMessage, ArgU16Message):
    opcode = 0xD2


class AseqMeta_LoadShortGateArray(MetaMessage, ArgU16Message):
    opcode = 0xD1


class AseqMeta_VoicePolicy(MetaMessage, ArgU8Message):
    opcode = 0xD0


class AseqMeta_Random(MetaMessage, ArgU8Message):
    opcode = 0xCE


class AseqMeta_DynCall(MetaMessage, ArgU16Message):
    opcode = 0xCD


class AseqMeta_LoadImmediate(MetaMessage, ArgU8Message):
    opcode = 0xCC


class AseqMeta_BitwiseAnd(MetaMessage, ArgU8Message):
    opcode = 0xC9


class AseqMeta_Subtract(MetaMessage, ArgU8Message):
    opcode = 0xC8


class AseqMeta_WriteSequenceScript(MetaMessage, ArgU8ArgU16Message):
    opcode = 0xC7


class AseqMeta_Stop(MetaMessage, NoArgsMessage):
    opcode = 0xC6


class AseqMeta_ScriptCounter(MetaMessage, ArgU16Message):
    opcode = 0xC5


class AseqMeta_RunSequence(MetaMessage, ArgU8ArgU8Message):
    opcode = 0xC4


class AseqMeta_MuteChannel(MetaMessage, ArgU16Message):
    opcode = 0xC3
    version = AseqVersion.MM
#endregion


#region Argbits
class AseqMeta_TestChannel(MetaMessage):
    opcode_range = range(0x00, 0x10)

    def __init__(self, ch: int):
        self.channel = ch

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        ch = cls.read_bits(data, offset, 4)
        return cls(ch)


class AseqMeta_StopChannel(MetaMessage):
    opcode_range = range(0x40, 0x50)

    def __init__(self, ch: int):
        self.channel = ch

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        ch = cls.read_bits(data, offset, 4)
        return cls(ch)


class AseqMeta_SubIO(MetaMessage):
    opcode_range = range(0x50, 0x58)

    def __init__(self, io: int):
        self.io_port = io

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        io = cls.read_bits(data, offset, 3)
        return cls(io)


class AseqMeta_LoadResource(MetaMessage):
    opcode_range = range(0x60, 0x70)
    size = 3

    def __init__(self, ch: int, arg_u8_1: int, arg_u8_2: int):
        self.channel = ch
        self.args = (ArgU8(arg_u8_1), ArgU8(arg_u8_2))

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        ch = cls.read_bits(data, offset, 4)
        arg_u8_1 = cls.read_u8(data, offset)
        arg_u8_2 = cls.read_u8(data, offset + 1)
        return cls(ch, arg_u8_1, arg_u8_2)


class AseqMeta_StoreIO(MetaMessage):
    opcode_range = range(0x70, 0x78)

    def __init__(self, io: int):
        self.io_port = io

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        io = cls.read_bits(data, offset, 3)
        return cls(io)


class AseqMeta_LoadIO(MetaMessage):
    opcode_range = range(0x80, 0x88)

    def __init__(self, io: int):
        self.io_port = io

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        io = cls.read_bits(data, offset, 3)
        return cls(io)


class AseqMeta_LoadChannel(MetaMessage):
    opcode_range = range(0x90, 0xA0)
    size = 3
    is_pointer = True

    def __init__(self, ch: int, arg_u16: int):
        self.channel = ch
        self.args = (ArgU16(arg_u16),)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        ch = cls.read_bits(data, offset, 4)
        arg_u16 = cls.read_u16(data, offset)
        return cls(ch, arg_u16)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}(ch={self.channel + 1}, arg_u16=0x{self.args[0].value:X})'


class AseqMeta_LoadChannelRelative(MetaMessage):
    opcode_range = range(0xA0, 0xB0)
    size = 3
    is_pointer = True

    def __init__(self, ch: int, arg_s16: int):
        self.channel = ch
        self.args = (ArgS16(arg_s16),)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        ch = cls.read_bits(data, offset, 4)
        arg_s16 = cls.read_s16(data, offset)
        return cls(ch, arg_s16)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}(ch={self.channel + 1}, arg_s16=0x{self.args[0].value:X})'


class AseqMeta_LoadSequence(MetaMessage):
    opcode_range = range(0xB0, 0xC0)
    size = 4
    is_pointer = True

    def __init__(self, ch: int, arg_u8: int, arg_u16: int):
        self.channel = ch
        self.args = (ArgU8(arg_u8), ArgU16(arg_u16))

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        ch = cls.read_bits(data, offset, 4)
        arg_u8 = cls.read_u8(data, offset)
        arg_u16 = cls.read_u16(data, offset + 1)
        return cls(ch, arg_u8, arg_u16)
#endregion