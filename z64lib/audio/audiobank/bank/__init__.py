"""
z64lib.audio.audiobank.banks
=====
"""

# Order matters, import non-dependents first, then dependents
from ._instrument_bank import InstrumentBank


__all__ = [
    "InstrumentBank",
]