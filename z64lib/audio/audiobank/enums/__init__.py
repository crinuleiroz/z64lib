"""
z64lib.audio.audiobank.enums
=====
"""

# Order matters, import non-dependents first, then dependents
from z64lib.audio.audiobank.enums.audio_sample_codec import AudioSampleCodec
from z64lib.audio.audiobank.enums.audio_storage_medium import AudioStorageMedium
from z64lib.audio.audiobank.enums.audio_cache_load_type import AudioCacheLoadType
from z64lib.audio.audiobank.enums.adsr_opcode import AdsrOpcode
from z64lib.audio.audiobank.enums.vadpcm_loop_count import VadpcmLoopCount


__all__ = [
    "AudioSampleCodec",
    "AudioStorageMedium",
    "AudioCacheLoadType",
    "AdsrOpcode",
    "VadpcmLoopCount",
]