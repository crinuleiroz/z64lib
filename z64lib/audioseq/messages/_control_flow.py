from z64lib.audioseq.messages import AseqMessage, NoArgsMessage, ArgU8Message, ArgU16Message, ArgVarMessage
from z64lib.core.enums import AseqSection


class AseqFlow_End(NoArgsMessage):
    """"""
    opcode = 0xFF
    is_terminal = True

    def __repr__(self):
        return f'AseqFlow_End(opcode=0xFF)'


class AseqFlow_Delay1(NoArgsMessage):
    """"""
    opcode = 0xFE


class AseqFlow_Delay(ArgVarMessage):
    """"""
    opcode = 0xFD
    sections = (AseqSection.META, AseqSection.CHAN)

    def __repr__(self):
        return f'AseqFlow_Delay(delay={hex(self.args[0].value)})'


class AseqFlow_Call(ArgU16Message):
    """"""
    opcode = 0xFC
    is_pointer = True


class AseqFlow_Jump(ArgU16Message):
    """"""
    opcode = 0xFB
    is_branch = True


class AseqFlow_BranchEqual(ArgU16Message):
    """"""
    opcode = 0xFA
    is_branch = True
    is_conditional = True


class AseqFlow_BranchLessThan(ArgU16Message):
    """"""
    opcode = 0xF9
    is_branch = True
    is_conditional = True


class AseqFlow_Loop(ArgU8Message):
    """"""
    opcode = 0xF8


class AseqFlow_LoopEnd(NoArgsMessage):
    """"""
    opcode = 0xF7


class AseqFlow_Break(NoArgsMessage):
    """"""
    opcode = 0xF6


class AseqFlow_BranchGreaterEqual(ArgU16Message):
    """"""
    opcode = 0xF5
    is_branch = True
    is_conditional = True


class AseqFlow_JumpRelative(ArgU8Message):
    """"""
    opcode = 0xF4
    is_branch = True
    is_conditional = True


class AseqFlow_JumpRelativeEqual(ArgU8Message):
    """"""
    opcode = 0xF3
    is_branch = True
    is_conditional = True


class AseqFlow_JumpRelativeLessThan(ArgU8Message):
    """"""
    opcode = 0xF2
    is_branch = True
    is_conditional = True