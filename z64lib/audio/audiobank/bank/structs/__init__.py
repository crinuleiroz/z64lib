"""
z64lib.audio.audiobank.banks.structs
=====
"""

# Order matters, import non-dependents first, then dependents
from ._envelope_struct import Envelope, EnvelopePoint
from ._vadpcm_book_struct import VadpcmBook, VadpcmBookHeader
from ._vadpcm_loop_struct import VadpcmLoop, VadpcmLoopHeader
from ._sample_struct import Sample, SampleFlags
from ._tuned_sample_struct import TunedSample
from ._instrument_struct import Instrument
from ._drum_struct import Drum


__all__ = [
    "EnvelopePoint",
    "Envelope",
    "VadpcmBookHeader",
    "VadpcmBook",
    "VadpcmLoopHeader",
    "VadpcmLoop",
    "SampleFlags",
    "Sample",
    "TunedSample",
    "Instrument",
    "Drum",
]