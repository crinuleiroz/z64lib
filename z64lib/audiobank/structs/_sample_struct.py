from z64lib.audiobank.structs import VadpcmLoop, VadpcmBook
from z64lib.core.enums import AudioSampleCodec, AudioStorageMedium
from z64lib.core.helpers import safe_enum
from z64lib.types import *


class Sample(Z64Struct):
    """
    Represents audio sample data in the instrument bank.

    .. code-block:: c

        typdef struct Sample {
            /* 0x00 */ u32 unk_0: 1;
            /* 0x00 */ u32 codec: 3;
            /* 0x00 */ u32 medium: 2;
            /* 0x00 */ u32 isCached: 1;
            /* 0x00 */ u32 isRelocated: 1;
            /* 0x00 */ u32 size: 24;
            /* 0x04 */ u8* sampleAddr;
            /* 0x08 */ u32 VadpcmLoop* loop;
            /* 0x0C */ u32 VadpcmBook* book;
        } Sample; // Size = 0x10

    Attributes
    ----------
    unk_0: int
        Unknown flag.
    codec: AudioSampleCodec
        The audio codec used to encode and decode the audio sample.
    medium: AudioStorageMedium
        The medium where the audio sample data is stored.
    is_cached: bool
        Flag indicating whether the audio sample is cached in memory.
    is_relocated: bool
        Flag indicating whether the audio sample is relocated in memory.
    size: int
        The total size of the audio sample's data in bytes.
    sample_addr: int
        An unsigned 32-bit integer pointing to the audio sample's data in
        the instrument bank's assigned `Audiotable`.
    loop: int
        An unsigned 32-bit integer pointing to a `VadpcmLoop` struct in the instrument bank.
    book: int
        An unsigned 32-bit integer pointing to a `VadpcmBook` struct in the instrument bank.
    """
    _fields_ = [
        ('flags', bitfield[u32, [
            ('unk_0', 1),
            ('codec', 3),
            ('medium', 2),
            ('is_cached', 1),
            ('is_relocated', 1),
            ('size', 24),
        ]]),
        ('sample_addr', u32),
        ('loop', pointer[VadpcmLoop]),
        ('book', pointer[VadpcmBook])
    ]
    # _align_ = 0x10
    _bool_fields_ = ['is_cached', 'is_relocated']
    _enum_fields_ = {
        'codec': AudioSampleCodec,
        'medium': AudioStorageMedium
    }