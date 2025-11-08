from z64lib.core.enums import NamedIntEnum


class AudioManagerDebugLevel(NamedIntEnum):
    """
    Represents the debugging level of the audio manager.

    .. code-block:: c

        typedef enum AudioManagerDebugLevel {
            /* 0 */ AUDIOMGR_DEBUG_LEVEL_NONE,
            /* 1 */ AUDIOMGR_DEBUG_LEVEL_NO_RSP,
            /* 2 */ AUDIOMGR_DEBUG_LEVEL_NO_UPDATE
        } AudioManagerDebugLevel;
    """
    NONE = 0
    """"""

    NO_RSP = 1
    """"""

    NO_UPDATE = 2
    """"""