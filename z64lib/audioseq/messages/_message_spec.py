import struct
from enum import Enum
from z64lib.audioseq.args import *
from z64lib.core.enums import AseqVersion, AseqSection


#region Base Message
class AseqMessage:
    opcode: int = 0x00
    opcode_range: range | None = None
    nbits: int | None = None
    args: tuple['AseqArg', ...] = ()
    arg_spec: list['ArgType'] = []
    size: int = 1
    is_terminal: bool = False
    is_branch: bool = False
    is_conditional: bool = False
    is_pointer: bool = False
    sections: tuple['AseqSection', ...] = (AseqSection.META, AseqSection.CHAN, AseqSection.LAYER)
    version: 'AseqVersion' = AseqVersion.BOTH

    # Argbits only come in 3 varieties
    bitmasks = {
        3: 0b00000111,
        4: 0b00001111,
        6: 0b00111111,
    }

    def get_arg(self, index: int, default=None, output_type=None):
        if 0 <= index < len(self.args):
            v = self.args[index].value
        else:
            v = default

        conv = {
            None: lambda v: v,
            'int': lambda v: int(v),
            'hex': lambda v: hex(int(v)),
            'bin': lambda v: bin(int(v)),
            'oct': lambda v: oct(int(v)),
        }

        if callable(output_type):
            return output_type(v)
        if isinstance(output_type, type):
            return output_type(v)
        if output_type in conv:
            return conv[output_type](v)

        raise ValueError()

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        raise NotImplementedError(f"{cls.__name__}.from_bytes is not implemented")

    @classmethod
    def read_bits(cls, data: bytes, offset: int, nbits: int = 4) -> int:
        if nbits not in cls.bitmasks:
            raise ValueError()
        return data[offset] & cls.bitmasks[nbits]

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
        ret = cls.read_u8(data, offset)
        if ret & 0x80:
            ret = ((ret << 8) & 0x7F00) | cls.read_u8(data, offset + 1)
            return ret, 2 # return arg_size, not msg_size
        return ret, 1 # return arg_size, not msg_size

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


#region Generic Message Types
class ArgType(Enum):
    u8  = (1, ArgU8)
    s8  = (1, ArgS8)
    u16 = (2, ArgU16)
    s16 = (2, ArgS16)
    var = (None, ArgVar)

    @property
    def arg_size(self):
        return self.value[0]

    @property
    def arg_cls(self):
        return self.value[1]


class GenericMessage(AseqMessage):
    """"""
    def __init__(self, *args, arg_bits: int | None = None, arg_sizes: list[int] | None = None):
        self.arg_bits = arg_bits
        self.args = tuple(spec.arg_cls(a) for spec, a in zip(self.arg_spec, args))

        if arg_sizes:
            self.size = 1 + sum(arg_sizes)
        else:
            self.size = 1 + sum(spec.arg_size for spec in self.arg_spec if spec.arg_size is not None)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        pos = offset
        values = []
        read_map = {
            ArgType.u8: cls.read_u8,
            ArgType.s8: cls.read_s8,
            ArgType.u16: cls.read_u16,
            ArgType.s16: cls.read_s16,
            ArgType.var: cls.read_argvar,
        }

        arg_bits = None
        if cls.nbits:
            arg_bits = cls.read_bits(data, offset, cls.nbits)

        arg_sizes = []
        for spec in cls.arg_spec:
            if spec == ArgType.var:
                val, size = read_map[spec](data, pos)
                values.append(val)
            else:
                val = read_map[spec](data, pos)
                size = spec.arg_size
                values.append(val)

            arg_sizes.append(size)
            pos += size

        return cls(*values, arg_bits=arg_bits, arg_sizes=arg_sizes)

    def __repr__(self):
        cls_name = self.__class__.__name__
        parts = []

        if hasattr(self, 'arg_bits') and self.arg_bits is not None:
            parts.append(f'arg_bits=0x{self.arg_bits:X}')
        if self.args:
            parts += [f'{a.__class__.__name__.lower()}=0x{a.value:X}' for a in self.args]
        if parts:
            return f'{cls_name}({', '.join(parts)})'

        return f'{cls_name}(opcode=0x{self.opcode:X})'


class ArgMessage(GenericMessage):
    nbits = None


class ArgbitMessage(GenericMessage):
    nbits = 4
#endregion


#region Special Message Types
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
#endregion

#region Section Message Types
class MetaMessage(AseqMessage):
    sections = (AseqSection.META,)


class ChanMessage(AseqMessage):
    sections = (AseqSection.CHAN,)


class NoteLayerMessage(AseqMessage):
    sections = (AseqSection.LAYER,)
#endregion


#region Message Registry
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
                section_dict.setdefault(opcode, []).append(msg)

    @classmethod
    def get_message_class(cls, section: AseqSection, opcode: int, version: AseqVersion, frag=None):
        candidates = cls._spec_by_section.get(section, {}).get(opcode, [])

        if not candidates:
            return None

        candidates = [
            c for c in candidates
            if c.version in (version, AseqVersion.BOTH)
        ]
        if not candidates:
            return None

        if section == AseqSection.LAYER and opcode < 0xC0:
            if frag is not None and hasattr(frag, "is_legato"):
                is_legato = frag.is_legato

                filtered = [
                    c for c in candidates
                    if getattr(c, "is_legato_type", None) == is_legato
                ]

                if filtered:
                    candidates = filtered

        return candidates[0] if candidates else None
#endregion