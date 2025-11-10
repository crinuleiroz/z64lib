import struct
from z64lib.audioseq.args import *
from z64lib.core.enums import AseqVersion, AseqSection


#region Base Class
class AseqMessage:
    opcode: int = 0x00
    opcode_range: range | None = None
    args: tuple['AseqArg', ...] = ()
    size: int = 1
    is_terminal: bool = False
    is_branch: bool = False
    is_conditional: bool = False
    is_pointer: bool = False
    sections: tuple['AseqSection', ...] = (AseqSection.META, AseqSection.CHAN, AseqSection.LAYER)
    version: 'AseqVersion' = AseqVersion.BOTH

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        return NotImplementedError

    @classmethod
    def read_u8(cls, data: bytes, offset: int) -> int:
        return struct.unpack_from('>B', data, offset + 1)[0]

    @classmethod
    def read_s8(cls, data: bytes, offset: int) -> int:
        return struct.unpack_from('>b', data, offset + 1)[0]

    @classmethod
    def read_u16(cls, data: bytes, offset: int) -> int:
        return struct.unpack_from('>H', data, offset + 1)[0]

    @classmethod
    def read_s16(cls, data: bytes, offset: int) -> int:
        return struct.unpack_from('>h', data, offset + 1)[0]

    @classmethod
    def read_argvar(cls, data: bytes, offset: int) -> tuple[int, int]:
        arglen = cls.read_u8(data, offset)

        if arglen & 0x80:
            val = cls.read_u16(data, offset)
            return val, 3
        else:
            return arglen, 2

    @classmethod
    def read_portamento(cls, data: bytes, offset: int) -> tuple[int, ...]:
        mode = cls.read_u8(data, offset)
        note = cls.read_u8(data, offset + 1)
        is_special = (mode & 0x80) != 0

        if is_special:
            time = cls.read_u8(data, offset + 2)
            size = 4
        else:
            val, var_size = cls.read_argvar(data, offset + 2)
            time = val
            size = 2 + var_size

        return mode, note, time, size
#endregion


#region Subclasses
class NoArgsMessage(AseqMessage):
    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        assert data[offset] == cls.opcode
        return cls()

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}(opcode=0x{self.opcode:X})'


class ArgU8Message(AseqMessage):
    size = 2

    def __init__(self, arg_u8: int):
        self.args = (ArgU8(arg_u8),)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        arg_u8 = cls.read_u8(data, offset)
        return cls(arg_u8)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}(arg_u8=0x{self.args[0].value:X})'


class ArgS8Message(AseqMessage):
    size = 2

    def __init__(self, arg_s8: int):
        self.args = (ArgU8(arg_s8),)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        arg_s8 = cls.read_s8(data, offset)
        return cls(arg_s8)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}(arg_s8=0x{self.args[0].value:X})'


class ArgU16Message(AseqMessage):
    size = 3

    def __init__(self, arg_u16: int):
        self.args = (ArgU16(arg_u16),)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        arg_u16 = cls.read_u16(data, offset)
        return cls(arg_u16)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}(arg_u16=0x{self.args[0].value:X})'


class ArgS16Message(AseqMessage):
    size = 3

    def __init__(self, arg_s16: int):
        self.args = (ArgS16(arg_s16),)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        arg_s16 = cls.read_s16(data, offset)
        return cls(arg_s16)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}(arg_s16=0x{self.args[0].value:X})'


class ArgU16_U8_Message(AseqMessage):
    size = 4

    def __init__(self, arg_u16: int, arg_u8: int):
        self.args = (ArgU16(arg_u16), ArgU8(arg_u8))

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        arg_u16 = cls.read_u16(data, offset)
        arg_u8 = cls.read_u8(data, offset + 2)
        return cls(arg_u16, arg_u8)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}(arg_u16=0x{self.args[0].value:X}, arg_u8=0x{self.args[1].value:X})'


class ArgVarMessage(AseqMessage):
    def __init__(self, arg_var: int, size: int):
        self.args = (ArgVar(arg_var),)
        self.size = size

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        arg_var, size = cls.read_argvar(data, offset)
        return cls(arg_var, size)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}(arg_var=0x{self.args[0].value:X})'


class PortamentoMessage(AseqMessage):
    def __init__(self, mode: int, note: int, time: int, size: int):
        self.args = (ArgU8(mode), ArgU8(note), ArgVar(time))
        self.size = size

    @classmethod
    def from_bytes(cls, data, offset):
        mode, note, time, size = cls.read_portamento(data, offset)
        return cls(mode, note, time, size)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}(mode=0x{self.args[0].value:X}, note=0x{self.args[1].value:X}, time=0x{self.args[2].value:X})'


class AseqMetaMessage(AseqMessage):
    sections = (AseqSection.META,)


class AseqChanMessage(AseqMessage):
    sections = (AseqSection.CHAN,)


class AseqLayerMessage(AseqMessage):
    sections = (AseqSection.LAYER,)
#endregion


#region Spec Class
class AseqMessageSpec:
    # mapping section -> opcode -> list of message classes
    _spec_by_section: dict[AseqSection, dict[int, list[type['AseqMessage']]]]= {
        sec: {} for sec in AseqSection
    }

    @classmethod
    def register(cls, msg: type['AseqMessage']):
        opcodes = []
        if msg.opcode_range is not None:
            opcodes = list(msg.opcode_range)
        else:
            opcodes = [msg.opcode]

        for section in msg.sections:
            section_dict = cls._spec_by_section[section]
            for opcode in opcodes:
                if opcode not in section_dict:
                    section_dict[opcode] = []
                section_dict[opcode].append(msg)

    @classmethod
    def get_message_class(cls, section: AseqSection, opcode: int, version: AseqVersion):
        candidates = cls._spec_by_section.get(section, {}).get(opcode, [])
        if version is None:
            return candidates[0] if candidates else None
        # pick the first candidate compatible with the version
        for c in candidates:
            if c.version == AseqVersion.BOTH or c.version == version:
                return c
        return None
#endregion