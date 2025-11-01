from z64lib.core.types import *
from z64lib.core.helpers import safe_enum

from z64lib.audio.enums import AudioStorageMedium, AudioCacheLoadType


class AudiobankIndexEntry(Z64Struct):
    """
    Represents an instrument bank's corresponding table entry.

    .. code-block:: c

        typdef struct AudiobankEntry {
            /* 0x00 */ uintptr_t romAddr;
            /* 0x04 */ size_t size;
            /* 0x08 */ s8 medium;
            /* 0x09 */ s8 cacheLoadType;
            /* 0x0A */ u8 sampleBankId1;
            /* 0x0B */ u8 sampleBankId2;
            /* 0x0C */ u8 numInstruments;
            /* 0x0D */ u8 numDrums;
            /* 0x0E */ s16 numEffects;
        } AudiobankEntry; // Size = 0x10
    """
    _fields_ = [
        ('rom_addr', u32),
        ('bank_size', u32),
        ('medium', s8),
        ('cache_load_type', s8),
        ('sample_bank_id_1', u8),
        ('sample_bank_id_2', u8),
        ('num_instruments', u8),
        ('num_drums', u8),
        ('num_effects', s16)
    ]
    _enum_fields_ = {
        'medium': AudioStorageMedium,
        'cache_load_type': AudioCacheLoadType
    }
    # _align_ = 0x10

    # Override from_bytes() because it is common to find truncated data
    @classmethod
    def from_bytes(cls, buffer: bytes, struct_offset: int = 0) -> 'AudiobankIndexEntry':
        """
        Parse an AudiobankIndexEntry from either a truncated (0x08) or full (0x10) Audiobank index entry.

        Truncated entries are used by Ocarina of Time Randomizer, Majora's Mask Randomizer, and OoTMM Randomizer.
        These truncated entries omit the offset to the instrument bank in Audiobank and the length of the instrument bank.
        """
        length = len(buffer)

        match length:
            case 0x08:
                buffer = (b'\x00' * 8) + buffer
            case 0x10:
                pass
            case _:
                raise ValueError(
                    f"Unexpected AudiobankIndexEntry size: {hex(length)} "
                    "(expected 0x08 or 0x10 bytes)."
                )

        return super().from_bytes(buffer, struct_offset)