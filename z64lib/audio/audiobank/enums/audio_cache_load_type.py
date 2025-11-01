from z64lib.core.enums import NamedIntEnum


class AudioCacheLoadType(NamedIntEnum):
    """
    Represents the possible audio cache load types.

    .. code-block:: c

        typedef enum AudioCacheLoadType {
            /* 0 */ CACHE_LOAD_PERMANENT,
            /* 1 */ CACHE_LOAD_PERSISTENT,
            /* 2 */ CACHE_LOAD_TEMPORARY,
            /* 3 */ CACHE_LOAD_EITHER,
            /* 4 */ CACHE_LOAD_EITHER_NOSYNC,
        } AudioSampleCodec;
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