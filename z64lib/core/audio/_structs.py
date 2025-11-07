from z64lib.core.helpers import safe_enum
from z64lib.core.types import *
from z64lib.core.enums import AdsrOpcode


class EnvelopePoint(Z64Struct):
    """
    Represents a entry in the envelope array, which can be either a time and amplitude pair
    or an opcode and index pair.

    .. code-block:: c

        typedef struct EnvelopePoint {
            /* 0x00 */ s16 timeOrOpcode;
            /* 0x02 */ s16 ampOrIndex;
        } EnvelopePoint; // Size = 0x04

    Attributes
    ----------
    time_or_opcode: int | AdsrOpcode
        If positive, represents time.
        If zero or negative, represents an ADSR opcode (see `AdsrOpcode`).
    amp_or_index: int
        If `time_or_opcode` is time, this value represents the amplitude change
        for the current point.
        If `time_or_opcode` is an opcode, this value represents the index of
        another point in the envelope array.
    is_opcode: bool
        True if `time_or_opcode` represents an opcode; False if it represents a time value.
    """
    _fields_ = [
        ('_time_or_opcode', s16),
        ('amp_or_index', s16)
    ]

    @property
    def time_or_opcode(self):
        val = self._time_or_opcode

        if val <= 0:
            return safe_enum(AdsrOpcode, val)
        else:
            return val

    @property
    def is_opcode(self):
        return self._time_or_opcode <= 0


class AdsrSettings(Z64Struct):
    """
    Represents the settings for the audio engines ADSR implementation.

    .. code-block:: c

        typedef struct AdsrSettings {
            /* 0x00 */ u8 decayIndex;
            /* 0x01 */ u8 sustain;
            /* 0x04 */ EnvelopePoint* envelope;
        } AdsrSettings; // size = 0x08

    Attributes
    ----------
    decay_index: int
        Index used to obtain the decay rate from the `adsrDecayTable`.
    sustain: int
        ...
    envelope: EnvelopePoint
        Pointer to an envelope array.
    """
    _fields_ = [
        ('decay_index', u8),
        ('sustain', u8),
        ('envelope', pointer(EnvelopePoint))
    ]
    _align_ = 4

class ReverbSettings(Z64Struct):
    """
    Represents the settings for the audio engine's reverb effect.

    .. code-block:: c

        typedef struct ReverbSettings {
            /* 0x00 */ u8 downsampleRate;
            /* 0x02 */ u16 windowSize;
            /* 0x04 */ u16 decayRatio;
            /* 0x04 */ u16 unk_06;
            /* 0x04 */ u16 unk_08;
            /* 0x04 */ u16 volume;
            /* 0x04 */ u16 leakRightToLeft;
            /* 0x04 */ u16 leakLeftToRight;
            /* 0x04 */ s8 unk_10;
            /* 0x04 */ u16 unk_12;
            /* 0x04 */ u16 lowPassFilterCutoffLeft;
            /* 0x04 */ u16 lowPassFilterCutoffRight;
        } ReverbSettings; // size = 0x18

    Attributes
    ----------
    downsample_rate: int
        ...
    window_size: int
        ...
    decay_ratio: int
        Determines the amount of reverb that persists.
    unk_06: int
        Unknown struct member.
    unk_08: int
        Unknown struct member.
    volume: int
        ...
    leak_right_to_left: int
        ...
    leak_left_to_right: int
        ...
    unk_10: int
        Unknown struct member.
    unk_12: int
        Unknown struct member.
    low_pass_filter_cutoff_left: int
        ...
    low_pass_filter_cutoff_right: int
        ...
    """
    _fields_ = [
        ('downsample_rate', u8),
        ('window_size', u16),
        ('decay_ratio', u16),
        ('unk_06', u16),
        ('unk_08', u16),
        ('volume', u16),
        ('leak_left_to_right', u16),
        ('leak_right_to_left', u16),
        ('unk_10', s8),
        ('unk_12', u16),
        ('low_pass_filter_cutoff_left', u16),
        ('low_pass_filter_cutoff_right', u16)
    ]


class AudioSpec(Z64Struct):
    """
    Represents high-level audio specifications.

    This data is requested when initializing or resetting the audio heap.

    .. code-block:: c

        typedef struct AudioSpec {
            /* 0x00 */ u32 sampleRate;
            /* 0x04 */ u8 unk_04;
            /* 0x05 */ u8 numVoices;
            /* 0x06 */ u8 numSeqPlayers;
            /* 0x07 */ u8 unk_07;
            /* 0x08 */ u8 unk_08;
            /* 0x09 */ u8 numReverbSettings;
            /* 0x0C */ ReverbSettings* reverbSettings;
            /* 0x10 */ u16 dmaSampleBufferSize1;
            /* 0x12 */ u16 dmaSampleBufferSize2;
            /* 0x14 */ u16 unk_14;
            /* 0x18 */ u32 persistentSeqCacheSize;
            /* 0x1C */ u32 persistentBankCacheSize;
            /* 0x20 */ u32 persistentSampleBankCacheSize;
            /* 0x24 */ u32 temporarySeqCacheSize;
            /* 0x28 */ u32 temporaryBankCacheSize;
            /* 0x2C */ u32 temporarySampleBankCacheSize;
            /* 0x30 */ u32 persistentSampleCacheSize;
            /* 0x34 */ u32 temporarySampleCacheSize;
        } AudioSpec; // size = 0x38

    Attributes
    ----------
    sample_rate: int
        Sample rate in Hz.
    unk_04: int
        Unknown struct member.
    num_voices: int
        Total number of voices that can sound simultaneously.
    num_seq_players: int
        Total number of sequence players used by the spec.
    unk_07: int
        Unknown struct member.
    unk_08: int
        Unknown struct member.
    num_reverb_settings: int
        Total number of reverb settings used by the spec.
    dma_sample_buffer_size_1: int
        Size of one of the temporary buffers used during audio sample decoding.
    dma_sample_buffer_size_2: int
        Size of one of the temporary buffers used during audio sample decoding.
    unk_14: int
        Unknown struct member.
    persistent_seq_cache_size: int
        Total size of the persistent audio sequence cache.
    persistent_bank_cache_size: int
        Total size of the persistent instrument bank cache.
    persistent_sample_bank_cache_size: int
        Total size of the persistent sample bank cache.
    temporary_seq_cache_size: int
        Total size of the temporary audio sequence cache.
    temporary_bank_cache_size: int
        Total size of the temporary instrument bank cache.
    temporary_sample_bank_cache_size: int
        Total size of the temporary sample bank cache.
    persistent_sample_cache_size: int
        Total size of the persistent audio sample cache.
    temporary_sample_cache_size: int
        Total size of the temporary audio sample cache.
    """
    _fields_ = [
        ('sample_rate', u32),
        ('unk_04', u8),
        ('num_voices', u8),
        ('num_seq_players', u8),
        ('unk_07', u8),
        ('unk_08', u8),
        ('num_reverb_settings', u8),
        ('reverb_settings', pointer(ReverbSettings)),
        ('dma_sample_buffer_size_1', u16),
        ('dma_sample_buffer_size_2', u16),
        ('unk_14', u16),
        ('persistent_seq_cache_size', u32),
        ('persistent_bank_cache_size', u32),
        ('persistent_sample_bank_cache_size', u32),
        ('temporary_seq_cache_size', u32),
        ('temporary_bank_cache_size', u32),
        ('temporary_sample_bank_cache_size', u32),
        ('persistent_sample_cache_size', u32),
        ('temporary_sample_cache_size', u32)
    ]


class TempoData(Z64Struct):
    """
    Represents [. . .].

    .. code-block:: c

        typedef struct TempoData {
            /* 0x00 */ s16 unk_00;
            /* 0x02 */ s16 seqTicksPerBeat;
        } TempoData; // size = 0x04

    Attributes
    ----------
    unk_00: int
        Unused struct member.
    seq_ppqn: int
        The ticks per beat in an audio sequence.
    """
    _fields_ = [
        ('unk_00', s16),
        ('seq_ppqn', s16)
    ]


class AudioHeapInitSizes(Z64Struct):
    """
    Represents the intial audio heap sizes.

    .. code-block:: c

        typedef struct AudioHeapInitSizes {
            /* 0x00 */ u32 heapSize;
            /* 0x04 */ u32 initPoolSize ;
            /* 0x08 */ u32 permanentPoolSize;
        } AudioHeapInitSizes; // size = 0x0C

    Attributes
    ----------
    heap_size: int
        Total bytes allocated to the audio heap.
        Must be less than or equal to the size of `gAudioHeap`.
    init_pool_size: int
        ...
    permanent_pool_size: int
        ...
    """
    _fields_ = [
        ('heap_size', u32),
        ('init_pool_size', u32),
        ('permanent_pool_size', u32)
    ]