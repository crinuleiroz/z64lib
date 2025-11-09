"""
z64lib.audioseq.messages
=====
"""

from ._message_spec import AseqMessage, AseqMessageSpec
from ._control_flow import (
    AseqFlow_End, AseqFlow_Delay1, AseqFlow_Delay, AseqFlow_Call,
    AseqFlow_Jump, AseqFlow_BranchEqual, AseqFlow_BranchLessThan,
    AseqFlow_Loop, AseqFlow_LoopEnd, AseqFlow_Break, AseqFlow_BranchGreaterEqual,
    AseqFlow_JumpRelative, AseqFlow_JumpRelativeEqual, AseqFlow_JumpRelativeLessThan
)
from ._meta import (
    AseqMeta_LoadChannel,
)
from ._channel import (
    AseqChannel_LoadLayer,
)
# from ._note_layer import (

# )

ALL_MESSAGES = [
    # Control Flow
    AseqFlow_End, AseqFlow_Delay1, AseqFlow_Delay, AseqFlow_Call,
    AseqFlow_Jump, AseqFlow_BranchEqual, AseqFlow_BranchLessThan,
    AseqFlow_Loop, AseqFlow_LoopEnd, AseqFlow_Break, AseqFlow_BranchGreaterEqual,
    AseqFlow_JumpRelative, AseqFlow_JumpRelativeEqual, AseqFlow_JumpRelativeLessThan,

    # Meta
    AseqMeta_LoadChannel,

    # Channel
    AseqChannel_LoadLayer,

    # Note Layer
]

__all__ = [
    # Message Spec
    "AseqMessage",
    "AseqMessageSpec",
    # Control Flow
    "AseqFlow_End",
    "AseqFlow_Delay1",
    "AseqFlow_Delay",
    "AseqFlow_Call",
    "AseqFlow_Jump",
    "AseqFlow_BranchEqual",
    "AseqFlow_BranchLessThan",
    "AseqFlow_Loop",
    "AseqFlow_LoopEnd",
    "AseqFlow_Break",
    "AseqFlow_BranchGreaterEqual",
    "AseqFlow_JumpRelative",
    "AseqFlow_JumpRelativeEqual",
    "AseqFlow_JumpRelativeLessThan",
    # Meta
    "AseqMeta_LoadChannel",
    # Channel
    "AseqChannel_LoadLayer",
    # Note Layer

    # Misc.
    "ALL_MESSAGES"
]