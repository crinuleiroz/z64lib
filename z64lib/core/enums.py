from enum import Enum, IntEnum


#region AdsrOpcode
class AdsrOpcode(IntEnum):
    """
    Represents available ADSR opcodes. Any value above 0 is treated as a value of time.

    #### ZeldaRET Decompilation
    ```c
    #define ADSR_DISABLE 0
    #define ADSR_HANG -1
    #define ADSR_GOTO -2
    #define ADSR_RESTART -3
    ```
    """
    DISABLE = 0
    """ Stops envelope processing. Notes are disabled and stop sounding immediately, bypassing their release phase. """

    HANG = -1
    """ Pauses envelope processing. Notes remain enabled and continue to sound until they enter their release phase. """

    GOTO = -2
    """ Jumps to the specified index in the envelope array. """

    RESTART = -3
    """ Restarts envelope processing. """
#endregion


#region AdsrStatus
class AdsrStatus(IntEnum):
    """
    Represents the possible ADSR states.

    #### ZeldaRET Decompilation
    ```c
    typedef enum AdsrStatus {
        /* 0 */ ADSR_STATE_DISABLED,
        /* 1 */ ADSR_STATE_INITIAL,
        /* 2 */ ADSR_STATE_START_LOOP,
        /* 3 */ ADSR_STATE_LOOP,
        /* 4 */ ADSR_STATE_FADE,
        /* 5 */ ADSR_STATE_HANG,
        /* 6 */ ADSR_STATE_DECAY,
        /* 7 */ ADSR_STATE_RELEASE,
        /* 8 */ ADSR_STATE_SUSTAIN,
    } AdsrStatus;
    ```
    """
    DISABLED = 0
    """"""

    INITIAL = 1
    """"""

    START_LOOP = 2
    """"""

    LOOP = 3
    """"""

    FADE = 4
    """"""

    HANG = 5
    """"""

    DECAY = 6
    """"""

    RELEASE = 7
    """"""

    SUSTAIN = 8
    """"""
#endregion


#region AseqSection
class AseqSection(Enum):
    META = 'metadata'
    CHAN = 'channel'
    LAYER = 'note_layer'
    # ARRAY = 'array'
    # TABLE = 'table'
    # ENVELOPE = 'envelope'
    # FILTER = 'filter'
    # UNK = 'unk'
#endregion


#region AseqVersion
class AseqVersion(IntEnum):
    OOT  = 0
    MM   = 1
    BOTH = 2
#endregion


#region AudioCacheLoadType
class AudioCacheLoadType(IntEnum):
    """
    Represents the possible audio cache load types.

    #### ZeldaRET Decompilation
    ```c
    typedef enum AudioCacheLoadType {
        /* 0 */ CACHE_LOAD_PERMANENT,
        /* 1 */ CACHE_LOAD_PERSISTENT,
        /* 2 */ CACHE_LOAD_TEMPORARY,
        /* 3 */ CACHE_LOAD_EITHER,
        /* 4 */ CACHE_LOAD_EITHER_NOSYNC,
    } AudioCacheLoadType;
    ```
    """
    LOAD_PERMANENT = 0
    """ Audio data is loaded into the permanent audio cache. """

    LOAD_PERSISTENT = 1
    """ Audio data is loaded into the persistent audio cache. """

    LOAD_TEMPORARY = 2
    """ Audio data is loaded into the temporary audio cache. """

    LOAD_EITHER = 3
    """ Audio data is loaded into either the persistent or temporary audio cache. """

    LOAD_EITHER_NOSYNC = 4
    """ Audio data is loaded into either the persistent or temporary audio cache without syncing. """
#endregion


#region AudioCacheType
class AudioCacheType(IntEnum):
    """
    Represents the possible audio cache types.

    #### ZeldaRET Decompilation
    ```c
    typedef enum AudioCacheType {
        /* 0 */ CACHE_TEMPORARY,
        /* 1 */ CACHE_PERSISTENT,
        /* 2 */ CACHE_EITHER,
        /* 3 */ CACHE_PERMANENT,
    } AudioCacheType;
    ```
    """
    TEMPORARY = 0
    """"""

    PERSISTENT = 1
    """"""

    EITHER = 2
    """"""

    PERMANENT = 3
    """"""
#endregion


#region AudioLoadStatus
class AudioLoadStatus(IntEnum):
    """
    Represents the possible audio load statuses.

    #### ZeldaRET Decompilation
    ```c
    typedef enum AudioLoadStatus {
        /* 0 */ LOAD_STATUS_NOT_LOADED,
        /* 1 */ LOAD_STATUS_LOADING,
        /* 2 */ LOAD_STATUS_LOADED,
        /* 3 */ LOAD_STATUS_DISCARDABLE,
        /* 4 */ LOAD_STATUS_LOW_PRIORITY,
        /* 5 */ LOAD_STATUS_PERMANENT,
    } AudioLoadStatus;
    ```
    """
    NOT_LOADED = 0
    """ The entry data is not loaded. """

    LOADING = 1
    """ The entry data is loading asynchronously. """

    LOADED = 2
    """ The entry data is loaded, may be discarded, and either no longer in use or memory is required by something else. """

    DISCARDABLE = 3
    """ The entry data is loaded and can safely be discarded. """

    LOW_PRIORITY = 4
    """ The entry data is loaded and is preferred for discarding over other loaded entries. (Instrument bank entries only.) """

    PERMANENT = 5
    """ The entry data is loaded into the permanent cache and will not be discarded. """
#endregion


#region AudioManagerDebugLevel
class AudioManagerDebugLevel(IntEnum):
    """
    Represents the debugging level of the audio manager.

    #### ZeldaRET Decompilation
    ```c
    typedef enum AudioManagerDebugLevel {
        /* 0 */ AUDIOMGR_DEBUG_LEVEL_NONE,
        /* 1 */ AUDIOMGR_DEBUG_LEVEL_NO_RSP,
        /* 2 */ AUDIOMGR_DEBUG_LEVEL_NO_UPDATE
    } AudioManagerDebugLevel;
    ```
    """
    NONE = 0
    """"""

    NO_RSP = 1
    """"""

    NO_UPDATE = 2
    """"""
#endregion


#region AudioSampleCodec
class AudioSampleCodec(IntEnum):
    """
    Represents the possible compression formats of an audio sample.

    #### ZeldaRET Decompilation
    ```c
    typedef enum AudioSampleCodec {
        /* 0 */ CODEC_ADPCM,
        /* 1 */ CODEC_S8,
        /* 2 */ CODEC_S16_INMEMORY,
        /* 3 */ CODEC_SMALL_ADPCM,
        /* 4 */ CODEC_REVERB,
        /* 5 */ CODEC_S16,
        /* 6 */ CODEC_UNK6, // Majora's Mask only
        /* 7 */ CODEC_UNK7 // Majora's Mask only
    } AudioSampleCodec;
    ```
    """
    ADPCM = 0
    """ 16 2-byte samples compressed into 4-bit samples. """

    S8 = 1
    """ 16 2-byte samples compressed into 8-bit samples. """

    S16_INMEMORY = 2
    """ 16 2-byte samples stored as uncompressed 16-bit samples in memory. """

    SMALL_ADPCM = 3
    """ 16 2-byte samples compressed into 2-bit samples. """

    REVERB = 4
    """  """

    S16 = 5
    """ 16 2-byte samples stored as uncompressed 16-bit samples. """

    UNK6 = 6 # Majora's Mask only
    """ Unknonwn. """

    UNK7 = 7 # Majora's Mask only
    """ Unknown uncompressed. """
#endregion


#region AudioStorageMedium
class AudioStorageMedium(IntEnum):
    """
    Represents the possible storage mediums of an audio sample.

    #### ZeldaRET Decompilation
    ```c
    typedef enum AudioStorageMedium {
        /* 0 */ MEDIUM_RAM,
        /* 1 */ MEDIUM_UNK,
        /* 2 */ MEDIUM_CART,
        /* 3 */ MEDIUM_DISK_DRIVE,
        /* 5 */ MEDIUM_RAM_UNLOADED = 5 // Majora's Mask only
    } AudioStorageMedium;
    ```
    """
    RAM = 0
    """ Data is stored in random-access memory. """

    UNK = 1
    """ Unknown. """

    CART = 2
    """ Data is stored in read-only memory on a cartridge. """

    DISK_DRIVE = 3
    """ Data is stored in read-only memory on a magnetic disk. """

    RAM_UNLOADED = 5 # Majora's Mask only
    """ Data is stored in random-access memory but has been unloaded. """
#endregion


#region AudiotableType
class AudiotableType(IntEnum):
    """
    Represents the possible audiotable types.

    #### ZeldaRET Decompilation
    typedef enum AudiotableType {
        /* 0 */ SEQUENCE_TABLE,
        /* 1 */ BANK_TABLE,
        /* 2 */ SAMPLE_TABLE,
    } AudiotableType;
    ```
    """
    SEQUENCE_TABLE = 0
    """ Audiotable contains audio sequence data. """

    BANK_TABLE = 1
    """ Audiotable contains instrument bank data. """

    SAMPLE_TABLE = 2
    """ Audiotable contains audio sample data. """
#endregion


#region SoundOutputMode
class SoundOutputMode(IntEnum):
    """
    Represents the possible sound output modes.

    #### ZeldaRET Decompilation
    typedef enum SoundOutputMode {
        /* 0 */ SOUND_OUTPUT_STEREO,
        /* 1 */ SOUND_OUTPUT_HEADSET,
        /* 2 */ SOUND_OUTPUT_SURROUND,
        /* 3 */ SOUND_OUTPUT_MONO,
    } SoundOutputMode;
    ```
    """
    STEREO = 0
    """"""

    HEADSET = 1
    """"""

    SURROUND = 2
    """"""

    MONO = 3
    """"""
#endregion


#region SoundSetting
class SoundSetting(IntEnum):
    """
    Represents the possible sound settings.

    #### ZeldaRET Decompilation
    ```c
    typedef enum SoundSetting {
        /* 0 */ SOUND_SETTING_STEREO,
        /* 1 */ SOUND_SETTING_MONO,
        /* 2 */ SOUND_SETTING_HEADSET,
        /* 3 */ SOUND_SETTING_SURROUND,
    } SoundSetting;
    ```
    """
    STEREO = 0
    """"""

    MONO = 1
    """"""

    HEADSET = 2
    """"""

    SURROUND = 3
    """"""
#endregion


#region VadpcmLoopCount
class VadpcmLoopCount(IntEnum):
    NO_LOOP = 0
    """ Represents an audio sample that plays once. """

    INDEFINITE_LOOP = 0xFFFFFFFF # 4294967295
    """ Represents an audio sample that plays indefinitely. """
#endregion


# Star Imports
__all__ = [
    'SoundSetting',
    'SoundOutputMode',
    'AudioSampleCodec',
    'AudioStorageMedium',
    'AudioCacheType',
    'AudioCacheLoadType',
    'AdsrStatus',
    'AdsrOpcode',
    'VadpcmLoopCount',
    'AudiotableType',
    'AudioLoadStatus',
    'AudioManagerDebugLevel',
    'AseqVersion',
    'AseqSection',
]
#endregion