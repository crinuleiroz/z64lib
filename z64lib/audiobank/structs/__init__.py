"""
z64lib.audio.audiobank.banks.structs
=====
"""

# Order matters, import non-dependents first, then dependents
from ._envelope_struct import Envelope
from ._vadpcm_book_struct import VadpcmBook, VadpcmBookHeader
from ._vadpcm_loop_struct import VadpcmLoop, VadpcmLoopHeader
from ._sample_struct import Sample
from ._tuned_sample_struct import TunedSample
from ._instrument_struct import Instrument
from ._drum_struct import Drum
from ._sound_effect_struct import SoundEffect


__all__ = [
    "Envelope",
    "VadpcmBookHeader",
    "VadpcmBook",
    "VadpcmLoopHeader",
    "VadpcmLoop",
    "Sample",
    "TunedSample",
    "Instrument",
    "Drum",
    "SoundEffect",
]