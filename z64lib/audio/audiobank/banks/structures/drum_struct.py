from z64lib.core.types import *

from z64lib.audio.audiobank.banks.structures import Envelope
from z64lib.audio.audiobank.banks.structures import TunedSample


class Drum(Z64Struct):
    """
    Represents drum data in the instrument bank.

    .. code-block:: c

        typdef struct Drum {
            /* 0x00 */ u8 decayIndex;
            /* 0x04 */ u8 pan;
            /* 0x08 */ u8 isRelocated;
            /* 0x04 */ TunedSample tunedSample;
            /* 0x0C */ struct Envelope* envelope;
        } Drum; // Size = 0x10
    """
    _fields_ = [
        ('decay_index', u8),
        ('pan', u8),
        ('is_relocated', u8),
        ('_pad', u8),
        ('tuned_sample', TunedSample),
        ('envelope', pointer(Envelope))
    ]
    _bool_fields_ = ['is_relocated']
    # _align_ = 0x10