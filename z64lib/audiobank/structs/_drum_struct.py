from z64lib.audiobank.structs import Envelope
from z64lib.audiobank.structs import TunedSample
from z64lib.types import *


class Drum(Z64Struct):
    """
    Represents drum data in the instrument bank.

    .. code-block:: c

        typdef struct Drum {
            /* 0x00 */ u8 decayIndex;
            /* 0x04 */ u8 pan;
            /* 0x08 */ u8 isRelocated;
            /* 0x0A */ TunedSample tunedSample;
            /* 0x0C */ struct Envelope* envelope;
        } Drum; // Size = 0x10

    Attributes
    ----------
    decay_index: int
        Index into the `AdsrDecayTable` used to determine the decay rate for
        the instrument's notes.
    pan: int
        Left-right panning for the drum's notes, where 0 = full left,
        64 = center, and 127 = full right.
    is_relocated: bool
        Flag indicating whether the instrument's data is relocated in memory.
    tuned_sample: TunedSample
        `TunedSample` object assigned to keys in the drum's notes.
    envelope: int
        An unsigned 32-bit integer pointing to an `Envelope` array in the instrument bank.
    """
    _fields_ = [
        ('decay_index', u8),
        ('pan', u8),
        ('is_relocated', u8),
        ('tuned_sample', TunedSample),
        ('envelope', pointer[Envelope])
    ]
    _bool_fields_ = ['is_relocated']
    # _align_ = 0x10