"""
z64lib.audio.audiobank
=====
"""

# Order matters, import non-dependents first, then dependents
from ._audiobank_index_entry import AudiobankIndexEntry
from ._audiobank_index import AudiobankIndex
from ._audiobank import Audiobank
from ._instrument_bank import InstrumentBank

__all__ = [
    "AudiobankIndexEntry",
    "AudiobankIndex",
    "Audiobank",
    "InstrumentBank",
]