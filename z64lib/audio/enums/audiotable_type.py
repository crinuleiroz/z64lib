from z64lib.core.enums import NamedIntEnum


class AudiotableType(NamedIntEnum):
    """
    Represents the possible audiotable types.

    .. code-block:: c

        typedef enum AudiotableType {
            /* 0 */ SEQUENCE_TABLE,
            /* 1 */ BANK_TABLE,
            /* 2 */ SAMPLE_TABLE,
        } AudiotableType;
    """
    SEQUENCE_TABLE = 0
    """ Audiotable contains audio sequence data. """

    BANK_TABLE = 1
    """ Audiotable contains instrument bank data. """

    SAMPLE_TABLE = 2
    """ Audiotable contains audio sample data. """