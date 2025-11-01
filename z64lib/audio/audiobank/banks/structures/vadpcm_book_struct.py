from z64lib.core.types import *


class VadpcmBookHeader(Z64Struct):
    """
    Represents the first 8 bytes of the VadpcmBook structure.

    .. code-block:: c

        typedef struct VadpcmBookHeader {
            /* 0x00 */ s32 order;
            /* 0x04 */ s32 numPredictors;
        } VadpcmBookHeader; // Size = 0x08
    """
    _fields_ = [
        ('order', s32),
        ('num_predictors', s32)
    ]


class VadpcmBook(Z64Struct):
    """
    Represents audio sample decoding information in the instrument bank.

    .. code-block:: c

        typedef struct VadpcmBook {
            /* 0x00 */ VadpcmBookHeader header;
            /* 0x08 */ s16 predictorCoeff[1];
        } VadpcmBook; // Size = 0x08 * header.order * header.numPredeictors
    """
    _fields_ = [
        ('header', VadpcmBookHeader),
        ('predictors', array(s16, 0))
    ]
    _align_ = 0x10

    @classmethod
    def from_bytes(cls, buffer: bytes, struct_offset: int = 0):
        obj = cls.__new__(cls)

        obj.header = VadpcmBookHeader.from_bytes(buffer, struct_offset)
        header_size = VadpcmBookHeader.size()

        order = obj.header.order
        num_predictors = obj.header.num_predictors
        total_coeff = 8 * order * num_predictors

        predictor_offset = struct_offset + header_size
        obj.predictors = array(s16, total_coeff).from_bytes(buffer, predictor_offset)

        return obj

    def __repr__(self):
        header_repr = repr(self.header).replace('\n', '\n  ')
        if not self.predictors or len(self.predictors) == 0:
            preds_repr = '[]'
        else:
            grouped = [
                ', '.join(f'{v}' for v in self.predictors[i:i+4])
                for i in range(0, len(self.predictors), 4)
            ]
            preds_repr = '[\n' + '\n'.join(f'    {line},' for line in grouped) + '\n  ]'

        return (
            f'{type(self).__name__}(\n'
            f'  header={header_repr}\n'
            f'  predictors={preds_repr}\n'
            f')'
        )