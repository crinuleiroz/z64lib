from z64lib.core.enums import AudioStorageMedium, AudioCacheLoadType
from z64lib.core.helpers import safe_enum
from z64lib.types import *


class AudiotableIndexEntry(Z64Struct):
    """
    Represents an audio table's corresponding entry.

    .. code-block:: c

        typedef struct AudiotableEntry {
            /* 0x00 */ uintptr_t romAddr;
            /* 0x04 */ size_t size;
            /* 0x08 */ s8 medium;
            /* 0x09 */ s8 cacheLoadType;
            /* 0x0A */ s16 shortData1;
            /* 0x0C */ s16 shortData2;
            /* 0x0E */ s16 shortData3;
        } AudiotableEntry; // size = 0x10

    Attributes
    ----------
    rom_addr: int
        Address of the entry in Audiotable.
    table_size: int
        Size of the Audiotable.
    medium: AudioStorageMedium
        The medium where the given data is stored.
    cache_load_type: AudioCacheLoadType
        The cache where the data loads into.
    short_data_1: int
        Unused.
    short_data_2: int
        Unused.
    short_data_3: int
        Unused.
    """
    _fields_ = [
        ('rom_addr', u32),
        ('table_size', u32),
        ('medium', s8),
        ('cache_load_type', s8),
        ('short_data_1', s16),
        ('short_data_2', s16),
        ('short_data_3', s16),
    ]
    _enums_ = {
        'medium': AudioStorageMedium,
        'cache_load_type': AudioCacheLoadType
    }
    # _align_ = 0x10