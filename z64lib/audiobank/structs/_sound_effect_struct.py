from z64lib.audiobank.structs import TunedSample
from z64lib.types import *

class SoundEffect(Z64Struct):
    """
    Represents sound effect data in an instrument bank.

    .. code-block:: c

        typedef struct SoundEffect {
            /* 0x00 */ TunedSample tunedSample;
        } SoundEffect; // size = 0x08

    Attributes
    ----------
    tuned_sample: TunedSample
        Pointless TunedSample wrapping found in ZeldaRET's codebase.
    """
    _fields_ = [
        ("tuned_sample", TunedSample)
    ]