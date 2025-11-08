from enum import Enum


class AseqSection(Enum):
    META = "metadata"
    CHAN = "channel"
    LAYER = "note_layer"


SECTION_ALL = (AseqSection.META, AseqSection.CHAN, AseqSection.LAYER)