from z64lib.core.types import *

from z64lib.audio.audiobank.bank.structs import TunedSample
from z64lib.audio.audiobank.bank.structs import Envelope


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
            /* 0x08 */ TunedSample lowRegionSample;
            /* 0x10 */ TunedSample primRegionSample;
            /* 0x18 */ TunedSample highRegionSample;
        } Instrument; // Size = 0x20

    Attributes
    ----------
    is_relocated: bool
        Flag indicating whether the instrument's data is relocated in memory.
    low_key_region: int
        A Zelda64 note value (MIDI - 21) that defines the boundary between the
        low and primary key regions.
    high_key_region: int
        A Zelda64 note value (MIDI - 21) that defines the boundary between the
        primary and high key regions.
    decay_index: int
        Index into the `AdsrDecayTable` used to determine the decay rate for
        the instrument's notes.
    envelope: int
        An unsigned 32-bit integer pointing to an `Envelope` array in the instrument bank.
    low_region_sample: TunedSample
        `TunedSample` object assigned to keys in the low key region.
    prim_region_sample: TunedSample
        `TunedSample` object assigned to keys in the primary key region.
    high_region_sample: TunedSample
        `TunedSample` object assigned to keys in the high key region.
    """
    _fields_ = [
        ('is_relocated', u8),
        ('low_key_region', u8),
        ('high_key_region', u8),
        ('decay_index', u8),
        ('envelope', pointer(Envelope)),
        ('low_region_sample', TunedSample),
        ('prim_region_sample', TunedSample),
        ('high_region_sample', TunedSample),
    ]
    _bool_fields_ = ['is_relocated']
    # _align_ = 0x10
