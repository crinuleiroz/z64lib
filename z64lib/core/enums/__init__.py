"""
z64lib.audio.audiobank.enums
=====
"""

# Order matters, import non-dependents first, then dependents
from ._named_int_enum import NamedIntEnum
from ._versioned_int_enum import VersionedIntEnum
from ._sound_setting import SoundSetting
from ._sound_output_mode import SoundOutputMode
from ._audio_sample_codec import AudioSampleCodec
from ._audio_storage_medium import AudioStorageMedium
from ._audio_cache_type import AudioCacheType
from ._audio_cache_load_type import AudioCacheLoadType
from ._adsr_status import AdsrStatus
from ._adsr_opcode import AdsrOpcode
from ._vadpcm_loop_count import VadpcmLoopCount
from ._audiotable_type import AudiotableType
from ._audio_load_status import AudioLoadStatus
from ._audio_manager_debug_level import AudioManagerDebugLevel
from ._aseq_version import AseqVersion
from ._aseq_opcode import AseqFlowOpcode, AseqMetaOpcode, AseqChanOpcode, AseqLayerOpcode
from ._aseq_sections import AseqSection, SECTION_ALL

__all__ = [
    "NamedIntEnum",
    "VersionedIntEnum",
    "SoundSetting",
    "SoundOutputMode",
    "AudioSampleCodec",
    "AudioStorageMedium",
    "AudioCacheType",
    "AudioCacheLoadType",
    "AdsrStatus",
    "AdsrOpcode",
    "VadpcmLoopCount",
    "AudiotableType",
    "AudioLoadStatus",
    "AudioManagerDebugLevel",
    "AseqVersion",
    "AseqFlowOpcode",
    "AseqMetaOpcode",
    "AseqChanOpcode",
    "AseqLayerOpcode",
    "AseqSection",
    "SECTION_ALL",
]