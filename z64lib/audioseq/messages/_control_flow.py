from z64lib.audioseq.messages import (
    ArgType,
    ArgMessage,
)
from z64lib.core.enums import AseqSection


class AseqFlow_End(ArgMessage):
    """"""
    opcode = 0xFF
    is_terminal = True


class AseqFlow_Delay1(ArgMessage):
    """"""
    opcode = 0xFE


class AseqFlow_Delay(ArgMessage):
    """"""
    opcode = 0xFD
    arg_spec = [ArgType.var]
    sections = (AseqSection.META, AseqSection.CHAN,)


class AseqFlow_Call(ArgMessage):
    """"""
    opcode = 0xFC
    arg_spec = [ArgType.u16]
    is_pointer = True


class AseqFlow_Jump(ArgMessage):
    """"""
    opcode = 0xFB
    arg_spec = [ArgType.u16]
    is_branch = True


class AseqFlow_BranchEqual(ArgMessage):
    """"""
    opcode = 0xFA
    arg_spec = [ArgType.u16]
    is_branch = True
    is_conditional = True


class AseqFlow_BranchLessThan(ArgMessage):
    """"""
    opcode = 0xF9
    arg_spec = [ArgType.u16]
    is_branch = True
    is_conditional = True


class AseqFlow_Loop(ArgMessage):
    """"""
    opcode = 0xF8
    arg_spec = [ArgType.u8]


class AseqFlow_LoopEnd(ArgMessage):
    """"""
    opcode = 0xF7


class AseqFlow_Break(ArgMessage):
    """"""
    opcode = 0xF6


class AseqFlow_BranchGreaterEqual(ArgMessage):
    """"""
    opcode = 0xF5
    arg_spec = [ArgType.u16]
    is_branch = True
    is_conditional = True


class AseqFlow_JumpRelative(ArgMessage):
    """"""
    opcode = 0xF4
    arg_spec = [ArgType.u8]
    is_branch = True
    is_conditional = True


class AseqFlow_JumpRelativeEqual(ArgMessage):
    """"""
    opcode = 0xF3
    arg_spec = [ArgType.u8]
    is_branch = True
    is_conditional = True


class AseqFlow_JumpRelativeLessThan(ArgMessage):
    """"""
    opcode = 0xF2
    arg_spec = [ArgType.u8]
    is_branch = True
    is_conditional = True