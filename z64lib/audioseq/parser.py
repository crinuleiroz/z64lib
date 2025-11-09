import struct
from z64lib.audioseq.sequence import *
from z64lib.audioseq.messages import *
from z64lib.core.enums import AseqVersion, AseqSection


class AseqParser:
    """"""
    def __init__(self, data: bytes, aseq_version: AseqVersion):
        assert aseq_version in (AseqVersion.OOT, AseqVersion.MM) # "BOTH" should not be used here

        self.data = data
        self.version = aseq_version
        self.sequence = AudioSequence(aseq_version)
        self.visited = set()
        self.queue: list[AseqFragment] = []

    def parse(self):
        """"""
        for msg in ALL_MESSAGES:
            AseqMessageSpec.register(msg)

        meta = AseqMetadata(0x0000)
        self.sequence.sections.append(meta)
        self.queue.append(meta)

        while self.queue:
            frag = self.queue.pop(0)
            if frag.addr in self.visited:
                continue
            self.visited.add(frag.addr)

            if isinstance(frag, AseqMessageFragment):
                self._parse_message_fragment(frag)
            elif isinstance(frag, AseqDataFragment):
                self._parse_data_fragment(frag)

            self._register_fragment(frag)

        return self.sequence

    def _parse_message_fragment(self, frag: AseqMessageFragment):
        """"""
        offset = frag.addr
        while offset < len(self.data):
            opcode = self.data[offset]
            section_type = self._infer_section(frag)
            msg_cls = AseqMessageSpec.get_message_class(section_type, opcode, self.version)

            if msg_cls is None:
                offset += 1
                continue

            msg = msg_cls.from_bytes(self.data, offset)
            frag.messages.append(msg)
            offset += msg.size

            self._handle_message_reference(frag, msg)

            if msg.is_terminal:
                break

    def _parse_data_fragment(self, frag: AseqDataFragment):
        """"""
        addr = frag.addr
        if isinstance(frag, AseqEnvelope):
            frag.data = []
            while True:
                delay, arg = struct.unpack_from('>2h', self.data, addr)
                if delay < 0:
                    break
                frag.data.append((delay, arg)) # Change to something more concrete later
        if isinstance(frag, AseqFilter):
            ...
        if isinstance(frag, AseqArray):
            ...
        if isinstance(frag, AseqTable):
            ...

    def _handle_message_reference(self, frag: AseqMessageFragment, msg: AseqMessage):
        """"""
        if isinstance(frag, AseqMetadata) and isinstance(msg, AseqMeta_LoadChannel):
            if frag.channels[msg.channel] is None:
                ch = Channel(msg.channel, msg.args[0].value)
                frag.channels[msg.channel] = ch
                self.queue.append(ch)

        if isinstance(frag, Channel) and isinstance(msg, AseqChannel_LoadLayer):
            if frag.note_layers[msg.note_layer] is None:
                ly = NoteLayer(msg.args[0].value)
                frag.note_layers[msg.note_layer] = ly
                self.queue.append(ly)

        if isinstance(msg, AseqFlow_Call):
            call_frag = AseqCall(msg.args[0].value)
            call_frag.parent_section = self._infer_section(frag)
            self.queue.append(call_frag)

        # Handle other fragment types later

    def _register_fragment(self, frag: AseqFragment):
        """"""
        if isinstance(frag, AseqCall):
            self.sequence.calls[frag.addr] = frag
        elif isinstance(frag, AseqTable):
            self.sequence.tables[frag.addr] = frag
        elif isinstance(frag, AseqEnvelope):
            self.sequence.envelopes[frag.addr] = frag
        elif isinstance(frag, AseqArray):
            self.sequence.arrays[frag.addr] = frag
        elif isinstance(frag, AseqFilter):
            self.sequence.filters[frag.addr] = frag

    def _infer_section(self, frag: AseqFragment) -> AseqSection:
        """"""
        if isinstance(frag, AseqMetadata):
            return AseqSection.META
        elif isinstance(frag, Channel):
            return AseqSection.CHAN
        elif isinstance(frag, NoteLayer):
            return AseqSection.LAYER
        elif isinstance(frag, AseqCall):
            return getattr(frag, 'parent_section', AseqSection.META)
        else:
            raise NotImplementedError

