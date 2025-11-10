"""
z64lib.audioseq.messages
=====
"""

from ._message_spec import (
    AseqMessage, NoArgsMessage, ArgU8Message, ArgS8Message,
    ArgU16Message, ArgS16Message, ArgU16_U8_Message, ArgVarMessage,
    PortamentoMessage, AseqMetaMessage, AseqChanMessage, AseqLayerMessage,
    AseqMessageSpec
)
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
from ._note_layer import (
    AseqLayer_DecayIndex, AseqLayer_Delay, AseqLayer_Envelope, AseqLayer_F0,
    AseqLayer_Instrument, AseqLayer_Legato, AseqLayer_NoDrumPan, AseqLayer_NoPortamento,
    AseqLayer_NotePan, AseqLayer_PitchBend2Semitones, AseqLayer_Portamento, AseqLayer_ShortDelay,
    AseqLayer_ShortGate, AseqLayer_ShortVelocity, AseqLayer_Staccato, AseqLayer_Stereo,
    AseqLayer_SurroundEffect, AseqLayer_Transpose
)

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
    AseqLayer_DecayIndex, AseqLayer_Delay, AseqLayer_Envelope, AseqLayer_F0,
    AseqLayer_Instrument, AseqLayer_Legato, AseqLayer_NoDrumPan, AseqLayer_NoPortamento,
    AseqLayer_NotePan, AseqLayer_PitchBend2Semitones, AseqLayer_Portamento, AseqLayer_ShortDelay,
    AseqLayer_ShortGate, AseqLayer_ShortVelocity, AseqLayer_Staccato, AseqLayer_Stereo,
    AseqLayer_SurroundEffect, AseqLayer_Transpose
]

__all__ = [
    # Message Spec
    "AseqMessage",
    "NoArgsMessage",
    "ArgU8Message",
    "ArgS8Message",
    "ArgU16Message",
    "ArgS16Message",
    "ArgU16_U8_Message",
    "ArgVarMessage",
    "PortamentoMessage",
    "AseqMetaMessage",
    "AseqChanMessage",
    "AseqLayerMessage",
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
    "AseqLayer_DecayIndex",
    "AseqLayer_Delay",
    "AseqLayer_Envelope",
    "AseqLayer_F0",
    "AseqLayer_Instrument",
    "AseqLayer_Legato",
    "AseqLayer_NoDrumPan",
    "AseqLayer_NoPortamento",
    "AseqLayer_NotePan",
    "AseqLayer_PitchBend2Semitones",
    "AseqLayer_Portamento",
    "AseqLayer_ShortDelay",
    "AseqLayer_ShortGate",
    "AseqLayer_ShortVelocity",
    "AseqLayer_Staccato",
    "AseqLayer_Stereo",
    "AseqLayer_SurroundEffect",
    "AseqLayer_Transpose",
    # Misc.
    "ALL_MESSAGES"
]