from z64lib.core.enums import NamedIntEnum


class AudioLoadStatus(NamedIntEnum):
    """
    Represents the possible audio load statuses.

    .. code-block:: c

        typedef enum AudioLoadStatus {
            /* 0 */ LOAD_STATUS_NOT_LOADED,
            /* 1 */ LOAD_STATUS_LOADING,
            /* 2 */ LOAD_STATUS_LOADED,
            /* 3 */ LOAD_STATUS_DISCARDABLE,
            /* 4 */ LOAD_STATUS_LOW_PRIORITY,
            /* 5 */ LOAD_STATUS_PERMANENT,
        } AudioLoadStatus;
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