from z64lib.core.enums import NamedIntEnum


class SoundSetting(NamedIntEnum):
    """
    Represents the possible sound settings.

    .. code-block:: c

        typedef enum SoundSetting {
            /* 0 */ SOUND_SETTING_STEREO,
            /* 1 */ SOUND_SETTING_MONO,
            /* 2 */ SOUND_SETTING_HEADSET,
            /* 3 */ SOUND_SETTING_SURROUND,
        } SoundSetting;
    """
    STEREO = 0
    """"""

    MONO = 1
    """"""

    HEADSET = 2
    """"""

    SURROUND = 3
    """"""