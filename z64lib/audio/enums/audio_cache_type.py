from z64lib.core.enums import NamedIntEnum


class AudioCacheType(NamedIntEnum):
    """
    Represents the possible audio cache types.

    .. code-block:: c

        typedef enum AudioCacheType {
            /* 0 */ CACHE_TEMPORARY,
            /* 1 */ CACHE_PERSISTENT,
            /* 2 */ CACHE_EITHER,
            /* 3 */ CACHE_PERMANENT,
        } AudioCacheType;
    """
    TEMPORARY = 0
    """"""

    PERSISTENT = 1
    """"""

    EITHER = 2
    """"""

    PERMANENT = 3
    """"""