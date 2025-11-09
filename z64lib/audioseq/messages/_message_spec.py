from z64lib.audioseq.args import *
from z64lib.core.enums import AseqVersion, AseqSection


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