from z64lib.core.types import *

from z64lib.audio.audiobank.banks.structures import Sample


class TunedSample(Z64Struct):
    """
    Represents a pitched sample in the instrument bank.

    .. code-block:: c

        typdef struct TunedSample {
            /* 0x00 */ Sample* sample;
            /* 0x04 */ f32 tuning;
        } TunedSample; // Size = 0x08
    """
    _fields_ = [
        ("sample", pointer(Sample)),
        ("tuning", f32)
    ]