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
    sample_bank_id_1: int
        Index of the primary audiotable in the audiotable index where the
        instrument bank's audio sample data is located.
    sample_bank_id_2: int
        Index of the secondart audiotable in the audiotable index where the
        instrument bank's audio sample data is located.
    num_instruments: int
        The total number of instruments in the instrument bank.
    num_drums: int
        The total number of drums in the instrument bank.
    num_effects: int
        The total number of sound effects in the instrument bank.
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
    def from_bytes(cls, buffer: bytes, struct_addr: int = 0) -> 'AudiobankIndexEntry':
        """
        Instantiates an `AudiobankIndexEntry` object from binary data.

        Entries may be truncated to 0x08 bytes, cutting out the address and size, because
        Ocarina of Time Randomizer, Majora's Mask Randomizer, and OoTMM Randomizer utilize
        truncated entries for their custom music files.

        Parameters
        ----------
        buffer: bytes
            Binary audiobank index entry data.
        struct_addr: int
            Address of the structure.

        Returns
        ----------
        AudiobankIndexEntry
            Returns a fully instantiated `AudiobankIndexEntry` object.

        Raises
        ----------
        ValueError
            Invalid index entry size, must be 0x08 or 0x10 bytes.
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

        return super().from_bytes(buffer, struct_addr)