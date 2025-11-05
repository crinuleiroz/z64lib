from z64lib.core.types import *
from z64lib.audio.enums import VadpcmLoopCount


class VadpcmLoopHeader(Z64Struct):
    """
    Represents the first 16 bytes of the VadpcmLoop structure.

    .. code-block:: c

        typedef struct VadpcmLoopHeader {
            /* 0x00 */ u32 loopStart;
            /* 0x04 */ u32 loopEnd;
            /* 0x08 */ u32 loopCount;
            /* 0x0C */ u32 numSamples;
        } VadpcmLoopHeader; // Size = 0x10

    Attributes
    ----------
    loop_start: int
        Offset, in samples, to the start of the loop.
    loop_end: int
        Offset, in samples, to the end of the loop.
    loop_count: VadpcmLoopCount
        Whether the sample loops indefinitely or just once.
    num_samples: int
        The total number of samples in the audio sample.
    """
    _fields_ = [
        ('loop_start', u32),
        ('loop_end', u32),
        ('loop_count', u32),
        ('num_samples', u32)
    ]
    _enum_fields_ = {
        'loop_count': VadpcmLoopCount
    }


class VadpcmLoop(Z64Struct):
    """
    Represents audio sample loop information in the instrument bank.

    .. code-block:: c

        typedef struct VadpcmLoop {
            /* 0x00 */ VadpcmLoopHeader header;
            /* 0x10 */ s16 predictorCoeff[16];
        } VadpcmLoop; // Size = 0x10 or 0x30

    Attributes
    ----------
    header: VadpcmLoopHeader
        Loop information for the audio sample.
    predictors: list[int]
        A list of signed prediction coefficient values.
    """
    _fields_ = [
        ('header', VadpcmLoopHeader),
        ('predictors', array(s16, 0))
    ]
    _dynamic_size_ = True

    # Override because the array is conditional based on header values
    @classmethod
    def from_bytes(cls, buffer: bytes, struct_offset:int = 0) -> 'VadpcmLoop':
        obj = cls.__new__(cls)

        obj.header = VadpcmLoopHeader.from_bytes(buffer, struct_offset)
        header_size = obj.header.size()

        if obj.header.loop_start == 0:
            obj.predictors = array(s16, 0)
        else:
            predictor_offset = struct_offset + header_size
            obj.predictors = array(s16, 16).from_bytes(buffer, predictor_offset)

        return obj

    def __repr__(self):
        header_repr = repr(self.header).replace('\n', '\n  ')
        if not self.predictors or len(self.predictors) == 0:
            preds = '[]'
        else:
            grouped = [
                ', '.join(f'{v}' for v in self.predictors[i:i+4])
                for i in range(0, len(self.predictors), 4)
            ]
            preds = '[\n' + '\n'.join(f'    {line},' for line in grouped) + '\n  ]'
        return (
            f'{type(self).__name__}(\n'
            f'  header={header_repr}\n'
            f'  predictors={preds}\n'
            f')'
        )