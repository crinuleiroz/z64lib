from z64lib.audiobank.structs import Sample
from z64lib.types import *


class TunedSample(Z64Struct):
    """
    Represents a pitched sample in the instrument bank.

    .. code-block:: c

        typdef struct TunedSample {
            /* 0x00 */ Sample* sample;
            /* 0x04 */ f32 tuning;
        } TunedSample; // Size = 0x08

    Attributes
    ----------
    sample: int
        An unsigned 32-bit integer pointing to a `Sample` struct in the instrument bank.
    tuning: float
        A 32-bit single-precision floating-point value used to pitch shift the
        audio sample during playback.
    """
    _fields_ = [
        ('sample', pointer[Sample]),
        ('tuning', f32)
    ]