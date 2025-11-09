from z64lib.audioseq.messages import AseqMessage


class AseqFragment:
    def __init__(self, addr: int):
        self.addr = addr
        self.parent_section = None


class AseqMessageFragment(AseqFragment):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.messages: list[AseqMessage] = []


class AseqDataFragment(AseqFragment):
    def __init__(self, addr: int, data: bytes | bytearray | None = None):
        super().__init__(addr)
        self.data = data


class NoteLayer(AseqMessageFragment):
    def __init__(self, addr: int):
        super().__init__(addr)


class Channel(AseqMessageFragment):
    def __init__(self, index: int, addr: int):
        super().__init__(addr)
        self.index = index
        self.note_layers: list[NoteLayer] = [None for _ in range(4)]

    def get_layer(self, index: int) -> NoteLayer | None:
        return self.note_layers[index] if 0 <= index <= 3 else None


class AseqMetadata(AseqMessageFragment):
    def __init__(self, addr: int):
        super().__init__(addr)
        self.channels: list[Channel] = [None for _ in range(16)]

    def get_channel(self, index: int) -> Channel | None:
        return self.channels[index] if 0 <= index <= 15 else None


class AseqCall(AseqMessageFragment): ...
class AseqArray(AseqDataFragment): ...
class AseqTable(AseqDataFragment): ...
class AseqEnvelope(AseqDataFragment): ...
class AseqFilter(AseqDataFragment): ...


class AudioSequence:
    def __init__(self, aseq_version):
        # ASEQ version
        self.version = aseq_version

        # Metadata sections
        self.sections: list[AseqMetadata] = []

        # Data fragments
        self.calls: dict[int, AseqCall] = {}
        self.arrays: dict[int, AseqArray] = {}
        self.tables: dict[int, AseqTable] = {}
        self.envelopes: dict[int, AseqEnvelope] = {}
        self.filters: dict[int, AseqFilter] = {}

        # Optional raw data
        self.data: bytes | bytearray | None = None