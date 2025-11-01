from z64lib.core.types import *

from z64lib.audio.audiobank.banks.structures import TunedSample
from z64lib.audio.audiobank.banks.structures import Envelope


class Instrument(Z64Struct):
    """
    Represents instrument data in the instrument bank.

    .. code-block:: c

        typdef struct Instrument {
            /* 0x00 */ u8 isRelocated;
            /* 0x01 */ u8 lowKeyRegion;
            /* 0x02 */ u8 highKeyRegion;
            /* 0x03 */ u8 decayIndex;
            /* 0x04 */ struct Envelope* envelope;
            /* 0x08 */ TunedSample lowKeyRegionSample;
            /* 0x10 */ TunedSample primKeyRegionSample;
            /* 0x18 */ TunedSample highKeyRegionSample;
        } Instrument; // Size = 0x20
    """
    _fields_ = [
        ('is_relocated', u8),
        ('low_key_region', u8),
        ('high_key_region', u8),
        ('decay_index', u8),
        ('envelope', pointer(Envelope)),
        ('low_key_region_sample', TunedSample),
        ('prim_key_region_sample', TunedSample),
        ('high_key_region_sample', TunedSample),
    ]
    _bool_fields_ = ['is_relocated']
    # _align_ = 0x10
