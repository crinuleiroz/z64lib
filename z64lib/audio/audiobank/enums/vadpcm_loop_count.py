from enum import IntEnum


class VadpcmLoopCount(IntEnum):
    NO_LOOP = 0
    """ Represents an audio sample that plays once. """

    INDEFINITE_LOOP = 0xFFFFFFFF # 4294967295
    """ Represents an audio sample that plays indefinitely. """