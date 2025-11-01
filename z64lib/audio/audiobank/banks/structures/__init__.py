"""
z64lib.audio.audiobank.banks.structures
=====
"""

# Order matters, import non-dependents first, then dependents
from .envelope_struct import Envelope, EnvelopePoint
from .vadpcm_book_struct import VadpcmBook, VadpcmBookHeader
from .vadpcm_loop_struct import VadpcmLoop, VadpcmLoopHeader
from .sample_struct import Sample, SampleFlags
from .tuned_sample_struct import TunedSample
from .instrument_struct import Instrument
from .drum_struct import Drum


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