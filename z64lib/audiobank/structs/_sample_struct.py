from z64lib.audiobank.structs import VadpcmLoop, VadpcmBook
from z64lib.core.enums import AudioSampleCodec, AudioStorageMedium
from z64lib.core.helpers import safe_enum
from z64lib.types import *


class SampleFlags:
    """ Represents a Sample struct's bitfield. """
    __slots__ = ('unk_0', '_codec', '_medium', '_is_cached', '_is_relocated', 'size')

    def __init__(self, unk_0, codec, medium, is_cached, is_relocated, size):
        self.unk_0 = unk_0
        self._codec = codec
        self._medium = medium
        self._is_cached = is_cached
        self._is_relocated = is_relocated
        self.size = size

    @property
    def codec(self):
        return safe_enum(AudioSampleCodec, self._codec)

    @property
    def medium(self):
        return safe_enum(AudioStorageMedium, self._medium)

    @property
    def is_cached(self):
        return bool(self._is_cached)

    @property
    def is_relocated(self):
        return bool(self._is_relocated)

    def __repr__(self):
        return (
            f'SampleFlags(\n'
            f'    unk_0={self.unk_0},\n'
            f'    codec={self.codec},\n'
            f'    medium={self.medium},\n'
            f'    is_cached={self.is_cached},\n'
            f'    is_relocated={self.is_relocated},\n'
            f'    size={self.size}\n'
            '  )'
        )


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
        ('flags', SampleFlags, [
            ('unk_0', u32, 1),
            ('codec', u32, 3),
            ('medium', u32, 2),
            ('is_cached', u32, 1),
            ('is_relocated', u32, 1),
            ('size', u32, 24),
        ]),
        ('sample_addr', u32),
        ('loop', pointer(VadpcmLoop)),
        ('book', pointer(VadpcmBook))
    ]
    # _align_ = 0x10
