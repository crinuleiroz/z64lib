from z64lib.core.enums import NamedIntEnum


class AdsrStatus(NamedIntEnum):
    """
    Represents the possible ADSR states.

    .. code-block:: c

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