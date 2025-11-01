from z64lib.core.enums import NamedIntEnum


class AudioStorageMedium(NamedIntEnum):
    """
    Represents the possible storage mediums of an audio sample.

    .. code-block:: c

        typedef enum AudioStorageMedium {
            /* 0 */ MEDIUM_RAM,
            /* 1 */ MEDIUM_UNK,
            /* 2 */ MEDIUM_CART,
            /* 3 */ MEDIUM_DISK_DRIVE,
            /* 5 */ MEDIUM_RAM_UNLOADED = 5
        } AudioStorageMedium;
    """
    RAM = 0
    """ Data is stored in random-access memory. """

    UNK = 1
    """ Unknown. """

    CART = 2
    """ Data is stored in read-only memory on a cartridge. """

    DISK_DRIVE = 3
    """ Data is stored in read-only memory on a magnetic disk. """

    RAM_UNLOADED = 5
    """ Data is stored in random-access memory but has been unloaded. """