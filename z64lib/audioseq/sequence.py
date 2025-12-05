from z64lib.audioseq.messages import AseqMessage


#region Null
class NullNoteLayer:
    """"""
    addr: int = -1
    messages: list[AseqMessage] = []
    is_null: bool = True

NULL_NOTE_LAYER = NullNoteLayer()


class NullChannel:
    """"""
    addr: int = -1
    messages: list[AseqMessage] = []
    note_layers: list['NoteLayer'] = []
    is_null: bool = True

    def get_layer(self, index: int):
        return NULL_NOTE_LAYER

NULL_CHANNEL = NullChannel()


class NullMetadata:
    """"""
    addr: int = -1
    channels: list['Channel'] = []
    is_null: bool = True

    def get_channel(self, index: int):
        return NULL_CHANNEL

NULL_METADATA = NullMetadata()
#endregion


#region Fragments
class AseqFragment:
    """"""
    def __init__(self, addr: int):
        self.addr = addr
        self.parent_section = None


class AseqMessageFragment(AseqFragment):
    """"""
    def __init__(self, addr: int):
        super().__init__(addr)
        self.messages: list[AseqMessage] = []


class AseqDataFragment(AseqFragment):
    """"""
    def __init__(self, addr: int, data: bytes | bytearray | None = None):
        super().__init__(addr)
        self.data = data


class NoteLayer(AseqMessageFragment):
    """"""
    is_null: bool = False

    def __init__(self, addr: int, is_legato: bool = False):
        super().__init__(addr)
        self.is_legato = is_legato


class Channel(AseqMessageFragment):
    """"""
    is_null: bool = False

    def __init__(self, index: int, addr: int):
        super().__init__(addr)
        self.is_legato = False
        self.index = index
        self.note_layers: list[NoteLayer] = [None for _ in range(4)]

    def get_layer(self, index: int) -> NoteLayer | NullNoteLayer:
        if 0 <= index < 4:# len(self.note_layers):
            return self.note_layers[index] or NULL_NOTE_LAYER
        return NULL_NOTE_LAYER


class AseqMetadata(AseqMessageFragment):
    """"""
    is_null: bool = False

    def __init__(self, addr: int):
        super().__init__(addr)
        self.channels: list[Channel] = [None for _ in range(16)]

    def get_channel(self, index: int) -> Channel | NullChannel:
        if 0 <= index < 16: #len(self.channels):
            return self.channels[index] or NULL_CHANNEL
        return NULL_CHANNEL


class AseqCall(AseqMessageFragment): ...
class AseqArray(AseqDataFragment): ...
class AseqTable(AseqDataFragment): ...
class AseqEnvelope(AseqDataFragment): ...
class AseqFilter(AseqDataFragment): ...
#endregion


#region AudioSequence
class AudioSequence:
    """"""
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

    def get_section(self, index: int) -> AseqMetadata | NullMetadata:
        """"""
        if 0 <= index < len(self.sections):
            return self.sections[index] or NULL_METADATA
        return NULL_METADATA
#endregion