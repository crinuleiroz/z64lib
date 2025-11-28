import struct
from enum import Enum
from z64lib.audioseq.args import *
from z64lib.core.enums import AseqVersion, AseqSection


#region Base Message
class AseqMessage:
    """"""
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
        """
        Retrieves the ASEQ message argument at the specified index.

        Parameters
        ----------
        index: int
            The index of the arg.
        default
            The default return value.
        output_type
            The output type for the return value (int, hex, bin, oct).

        Returns
        ----------
        output_type | int
            The arg's value, or the default return value if the arg
            can not be retrieved.
        """
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
        """
        Reads the opcode of an ASEQ message at the specified offset and returns
        the bitmasked value.

        Parameters
        ----------
        data: bytes
            Binary audio sequence data.
        offset: int
            The address of the ASEQ message.
        nbits: int
            The total number of bits the arg embedded in the opcode takes.

        Returns
        ----------
        int
            The value of the arg embedded in the opcode.
        """
        if nbits not in cls.bitmasks:
            raise ValueError()
        return data[offset] & cls.bitmasks[nbits]

    @classmethod
    def read_u8(cls, data: bytes, offset: int) -> int:
        """
        Reads one bytes of binary sequence data at the specified offset,
        skipping the opcode byte, and returns its integer value (unsigned).

        Parameters
        ----------
        data: bytes
            Binary audio sequence data.
        offset: int
            The address of the ASEQ message.

        Returns
        ----------
        int
            The arg value as an unsigned integer.
        """
        return struct.unpack_from('>B', data, offset + 1)[0]

    @classmethod
    def read_s8(cls, data: bytes, offset: int) -> int:
        """
        Reads one bytes of binary sequence data at the specified offset,
        skipping the opcode byte, and returns its integer value (signed).

        Parameters
        ----------
        data: bytes
            Binary audio sequence data.
        offset: int
            The address of the ASEQ message.

        Returns
        ----------
        int
            The arg value as a signed integer.
        """
        return struct.unpack_from('>b', data, offset + 1)[0]

    @classmethod
    def read_u16(cls, data: bytes, offset: int) -> int:
        """
        Reads two bytes of binary sequence data at the specified offset,
        skipping the opcode byte, and returns its integer value (unsigned).

        Parameters
        ----------
        data: bytes
            Binary audio sequence data.
        offset: int
            The address of the ASEQ message.

        Returns
        ----------
        int
            The arg value as an unsigned integer.
        """
        return struct.unpack_from('>H', data, offset + 1)[0]

    @classmethod
    def read_s16(cls, data: bytes, offset: int) -> int:
        """
        Reads two bytes of binary sequence data at the specified offset,
        skipping the opcode byte, and returns its integer value (signed).

        Parameters
        ----------
        data: bytes
            Binary audio sequence data.
        offset: int
            The address of the ASEQ message.

        Returns
        ----------
        int
            The arg value as a signed integer.
        """
        return struct.unpack_from('>h', data, offset + 1)[0]

    @classmethod
    def read_argvar(cls, data: bytes, offset: int) -> tuple[int, int]:
        """
        Reads the bytes for an `ArgVar` ASEQ message type at the specified
        offset and converts it to an integer value.

        `ArgVar` ASEQ messages are variable sized. There is always at least one
        byte. However, if the byte is 0x80 (128) or above, then the length of the
        message is increased by a byte, with the MSB set to at least 0x80.

        Parameters
        ----------
        data: bytes
            Binary audio sequence data.
        offset: int
            The address of the ASEQ message.

        Returns
        ----------
        tuple[int, int]
            A tuple containing the arg value, and the arg size.
        """
        ret = cls.read_u8(data, offset)
        if ret & 0x80:
            ret = ((ret << 8) & 0x7F00) | cls.read_u8(data, offset + 1)
            return ret, 2 # return arg_size, not msg_size
        return ret, 1 # return arg_size, not msg_size

    @classmethod
    def read_portamento(cls, data: bytes, offset: int) -> tuple[int, ...]:
        """
        Reads the bytes for the portamento type ASEQ messages at the specified offset
        and converts its args to int.

        Parameters
        ----------
        data: bytes
            Binary audio sequence data.
        offset: int
            The address of the ASEQ message.

        Returns
        ----------
        tuple[int, ...]
            A tuple containing the portamento message's arg values and total arg data size.
        """
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
    """ An unsigned 8-bit integer. """

    s8  = (1, ArgS8)
    """ A signed 8-bit integer. """

    u16 = (2, ArgU16)
    """ An unsigned 16-bit integer. """

    s16 = (2, ArgS16)
    """ A signed 16-bit integer. """

    var = (None, ArgVar)
    """ A variable-length unsigned integer. """

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
        """"""
        pos = offset
        values = []
        read_map = {
            ArgType.u8: cls.read_u8,
            ArgType.s8: cls.read_s8,
            ArgType.u16: cls.read_u16,
            ArgType.s16: cls.read_s16,
            ArgType.var: cls.read_argvar,
        }

        # Handle argbit types
        arg_bits = None
        if cls.nbits:
            arg_bits = cls.read_bits(data, offset, cls.nbits)

        # Handle u8, s8, u16, s16, and var types
        arg_sizes = []
        for spec in cls.arg_spec:
            # Special handling for variable-length types
            if spec == ArgType.var:
                val, size = read_map[spec](data, pos)
                values.append(val)
            else:
                val = read_map[spec](data, pos)
                size = spec.arg_size
                values.append(val)

            arg_sizes.append(size)
            pos += size # Increase position by arg_size

        return cls(*values, arg_bits=arg_bits, arg_sizes=arg_sizes)

    def __repr__(self):
        cls_name = self.__class__.__name__
        parts = []

        if hasattr(self, 'arg_bits') and self.arg_bits is not None:
            parts.append(f"arg_bits=0x{self.arg_bits:X}")
        if self.args:
            parts += [f"{a.__class__.__name__.lower()}=0x{a.value:X}" for a in self.args]
        if parts:
            return f"{cls_name}({', '.join(parts)})"

        return f"{cls_name}(opcode=0x{self.opcode:X})"


class ArgMessage(GenericMessage):
    """"""
    nbits = None


class ArgbitMessage(GenericMessage):
    """"""
    nbits = 4
#endregion


#region Special Message Types
class PortamentoMessage(AseqMessage):
    """"""
    def __init__(self, mode: int, note: int, time: int, size: int):
        self.args = (ArgU8(mode), ArgU8(note), ArgVar(time))
        self.size = size

    @classmethod
    def from_bytes(cls, data, offset):
        """"""
        mode, note, time, size = cls.read_portamento(data, offset)
        return cls(mode, note, time, size)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}(mode=0x{self.args[0].value:X}, note=0x{self.args[1].value:X}, time=0x{self.args[2].value:X})'
#endregion

#region Section Message Types
class MetaMessage(AseqMessage):
    """ An ASEQ message available in the audio sequence's metadata. """
    sections = (AseqSection.META,)


class ChanMessage(AseqMessage):
    """ An ASEQ message available in the audio sequence's channels. """
    sections = (AseqSection.CHAN,)


class NoteLayerMessage(AseqMessage):
    """ An ASEQ message available in the audio sequence's note layers. """
    sections = (AseqSection.LAYER,)
#endregion


#region Message Registry
class AseqMessageSpec:
    """"""
    # mapping section -> opcode -> list of message classes
    _spec_by_section: dict[AseqSection, dict[int, list[type['AseqMessage']]]]= {
        sec: {} for sec in AseqSection
    }

    @classmethod
    def register(cls, msg: type['AseqMessage']):
        """"""
        opcodes = []

        # Argbit message types occupy a range of values.
        # The lower n bits determine the final opcode value,
        # while the higher bits determine the overall opcode type
        # similar to MIDI status bytes.
        if msg.opcode_range is not None:
            opcodes = list(msg.opcode_range)
        else:
            opcodes = [msg.opcode]

        # Filter the messages into their respective section dictionary
        for section in msg.sections:
            section_dict = cls._spec_by_section[section]
            for opcode in opcodes:
                section_dict.setdefault(opcode, []).append(msg)

    @classmethod
    def get_message_class(cls, section: AseqSection, opcode: int, version: AseqVersion, frag=None):
        """"""
        # Retrieve the message from the given section with the given opcode
        candidates = cls._spec_by_section.get(section, {}).get(opcode, [])

        if not candidates:
            return None

        # Filter the list by version
        candidates = [
            c for c in candidates
            if c.version in (version, AseqVersion.BOTH)
        ]
        if not candidates:
            return None

        # Like MIDI, Zelda64 has different note modes. However,
        # the note modes in Zelda64 handle the defaults at the
        # metadata/channel/layer level instead of globally.
        if section == AseqSection.LAYER and opcode < 0xC0:
            if frag is not None and hasattr(frag, 'is_legato'):
                is_legato = frag.is_legato

                # If legato, remove staccato, and vice versa
                filtered = [
                    c for c in candidates
                    if getattr(c, 'is_legato_type', None) == is_legato
                ]

                if filtered:
                    candidates = filtered

        return candidates[0] if candidates else None
#endregion