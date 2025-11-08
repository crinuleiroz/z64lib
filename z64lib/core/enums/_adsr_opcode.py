from z64lib.core.enums import NamedIntEnum

class AdsrOpcode(NamedIntEnum):
    """
    Represents available ADSR opcodes. Any value above 0 is treated as a value of time.

    .. code-block:: c

        #define ADSR_DISABLE 0
        #define ADSR_HANG -1
        #define ADSR_GOTO -2
        #define ADSR_RESTART -3
    """
    DISABLE = 0
    """ Stops envelope processing. Notes are disabled and stop sounding immediately, bypassing their release phase. """

    HANG = -1
    """ Pauses envelope processing. Notes remain enabled and continue to sound until they enter their release phase. """

    GOTO = -2
    """ Jumps to the specified index in the envelope array. """

    RESTART = -3
    """ Restarts envelope processing. """