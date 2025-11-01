from z64lib.core.enums import NamedIntEnum


class AudioSampleCodec(NamedIntEnum):
    """
    Represents the possible compression formats of an audio sample.

    .. code-block:: c

        typedef enum AudioSampleCodec {
            /* 0 */ CODEC_ADPCM,
            /* 1 */ CODEC_S8,
            /* 2 */ CODEC_S16_INMEM,
            /* 3 */ CODEC_SMALL_ADPCM,
            /* 4 */ CODEC_REVERB,
            /* 5 */ CODEC_S16,
            /* 6 */ CODEC_UNK6,
            /* 7 */ CODEC_UNK7
        } AudioSampleCodec;
    """
    ADPCM = 0
    """ 16 2-byte samples compressed into 4-bit samples. """

    S8 = 1
    """ 16 2-byte samples compressed into 8-bit samples. """

    S16_INMEM = 2
    """ 16 2-byte samples stored as uncompressed 16-bit samples in memory. """

    SMALL_ADPCM = 3
    """ 16 2-byte samples compressed into 2-bit samples. """

    REVERB = 4
    """  """

    S16 = 5
    """ 16 2-byte samples stored as uncompressed 16-bit samples. """

    UNK6 = 6
    """ Unknonwn. """

    UNK7 = 7
    """ Unknown uncompressed. """