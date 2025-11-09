import struct
from z64lib.audioseq.args import *
from z64lib.audioseq.messages import AseqMessage
from z64lib.core.enums import AseqSection


class AseqFlow_End(AseqMessage):
    """"""
    opcode = 0xFF
    is_terminal = True

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        assert data[offset] == cls.opcode
        return cls()

    def __repr__(self):
        return f'AseqFlow_End(opcode=0xFF)'


class AseqFlow_Delay1(AseqMessage):
    """"""
    opcode = 0xFE

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        assert data[offset] == cls.opcode
        return cls()


class AseqFlow_Delay(AseqMessage):
    """"""
    opcode = 0xFD
    sections = (AseqSection.META, AseqSection.CHAN)

    def __init__(self, value: int, size: int):
        self.args = (ArgVar(value),)
        self.size = size

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        arglen = data[offset + 1]

        if arglen & 0x80:
            _, val = struct.unpack_from('>BH', data, offset)
            return cls(val, size=3)
        else:
            _, val = struct.unpack_from('>2B', data, offset)
            return cls(val, size=2)

    def __repr__(self):
        return f'AseqFlow_Delay(delay={hex(self.args[0].value)})'


class AseqFlow_Call(AseqMessage):
    """"""
    opcode = 0xFC
    size = 3
    is_pointer = True

    def __init__(self, value: int):
        self.args = (ArgU16(value),)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        _, val = struct.unpack_from('>BH', data, offset)
        return cls(val)


class AseqFlow_Jump(AseqMessage):
    """"""
    opcode = 0xFB
    size = 3
    is_branch = True

    def __init__(self, value: int):
        self.args = (ArgU16(value),)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        _, val = struct.unpack_from('>BH', data, offset)
        return cls(val)


class AseqFlow_BranchEqual(AseqMessage):
    """"""
    opcode = 0xFA
    size = 3
    is_branch = True
    is_conditional = True

    def __init__(self, value: int):
        self.args = (ArgU16(value),)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        _, val = struct.unpack_from('>BH', data, offset)
        return cls(val)


class AseqFlow_BranchLessThan(AseqMessage):
    """"""
    opcode = 0xF9
    size = 3
    is_branch = True
    is_conditional = True

    def __init__(self, value: int):
        self.args = (ArgU16(value),)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        _, val = struct.unpack_from('>BH', data, offset)
        return cls(val)


class AseqFlow_Loop(AseqMessage):
    """"""
    opcode = 0xF8
    size = 2

    def __init__(self, value: int):
        self.args = (ArgU8(value),)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        _, val = struct.unpack_from('>2B', data, offset)
        return cls(val)


class AseqFlow_LoopEnd(AseqMessage):
    """"""
    opcode = 0xF7

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        assert data[offset] == cls.opcode
        return cls()


class AseqFlow_Break(AseqMessage):
    """"""
    opcode = 0xF6

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        assert data[offset] == cls.opcode
        return cls()


class AseqFlow_BranchGreaterEqual(AseqMessage):
    """"""
    opcode = 0xF5
    size = 3
    is_branch = True
    is_conditional = True

    def __init__(self, value: int):
        self.args = (ArgU16(value),)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        return super().from_bytes(data, offset)


class AseqFlow_JumpRelative(AseqMessage):
    """"""
    opcode = 0xF4
    size = 2
    is_branch = True
    is_conditional = True

    def __init__(self, value: int):
        self.args = (ArgU8(value),)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        _, val = struct.unpack_from('>2B', data, offset)
        return cls(val)


class AseqFlow_JumpRelativeEqual(AseqMessage):
    """"""
    opcode = 0xF3
    size = 2
    is_branch = True
    is_conditional = True

    def __init__(self, value: int):
        self.args = (ArgU8(value),)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        _, val = struct.unpack_from('>2B', data, offset)
        return cls(val)


class AseqFlow_JumpRelativeLessThan(AseqMessage):
    """"""
    opcode = 0xF2
    size = 2
    is_branch = True
    is_conditional = True

    def __init__(self, value: int):
        self.args = (ArgU8(value),)

    @classmethod
    def from_bytes(cls, data: bytes, offset: int):
        _, val = struct.unpack_from('>2B', data, offset)
        return cls(val)