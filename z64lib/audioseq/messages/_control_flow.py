from z64lib.audioseq.messages import (
    AseqMessage, NoArgsMessage, ArgU8Message, ArgS8Message,
    ArgU16Message, ArgS16Message, ArgVarMessage, PortamentoMessage
)
from z64lib.core.enums import AseqSection


class AseqFlow_End(AseqMessage, NoArgsMessage):
    """"""
    opcode = 0xFF
    is_terminal = True

    def __repr__(self):
        return f'AseqFlow_End(opcode=0xFF)'


class AseqFlow_Delay1(AseqMessage, NoArgsMessage):
    """"""
    opcode = 0xFE


class AseqFlow_Delay(AseqMessage, ArgVarMessage):
    """"""
    opcode = 0xFD
    sections = (AseqSection.META, AseqSection.CHAN)

    def __repr__(self):
        return f'AseqFlow_Delay(delay={hex(self.args[0].value)})'


class AseqFlow_Call(AseqMessage, ArgU16Message):
    """"""
    opcode = 0xFC
    is_pointer = True


class AseqFlow_Jump(AseqMessage, ArgU16Message):
    """"""
    opcode = 0xFB
    is_branch = True


class AseqFlow_BranchEqual(AseqMessage, ArgU16Message):
    """"""
    opcode = 0xFA
    is_branch = True
    is_conditional = True


class AseqFlow_BranchLessThan(AseqMessage, ArgU16Message):
    """"""
    opcode = 0xF9
    is_branch = True
    is_conditional = True


class AseqFlow_Loop(AseqMessage, ArgU8Message):
    """"""
    opcode = 0xF8


class AseqFlow_LoopEnd(AseqMessage, NoArgsMessage):
    """"""
    opcode = 0xF7


class AseqFlow_Break(AseqMessage, NoArgsMessage):
    """"""
    opcode = 0xF6


class AseqFlow_BranchGreaterEqual(AseqMessage, ArgU16Message):
    """"""
    opcode = 0xF5
    is_branch = True
    is_conditional = True


class AseqFlow_JumpRelative(AseqMessage, ArgU8Message):
    """"""
    opcode = 0xF4
    is_branch = True
    is_conditional = True


class AseqFlow_JumpRelativeEqual(AseqMessage, ArgU8Message):
    """"""
    opcode = 0xF3
    is_branch = True
    is_conditional = True


class AseqFlow_JumpRelativeLessThan(AseqMessage, ArgU8Message):
    """"""
    opcode = 0xF2
    is_branch = True
    is_conditional = True