from z64lib.core.enums import NamedIntEnum


class SoundOutputMode(NamedIntEnum):
    """
    Represents the possible sound output modes.

    .. code-block:: c

        typedef enum SoundOutputMode {
            /* 0 */ SOUND_OUTPUT_STEREO,
            /* 1 */ SOUND_OUTPUT_HEADSET,
            /* 2 */ SOUND_OUTPUT_SURROUND,
            /* 3 */ SOUND_OUTPUT_MONO,
        } SoundOutputMode;
    """
    STEREO = 0
    """"""

    HEADSET = 1
    """"""

    SURROUND = 2
    """"""

    MONO = 3
    """"""