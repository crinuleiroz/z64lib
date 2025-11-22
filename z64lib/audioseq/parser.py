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

        # Register messages to their dictionaries
        for msg in ALL_MESSAGES:
            AseqMessageSpec.register(msg)

        # Create and queue the sequence metadata
        meta = AseqMetadata(0x0000)
        self.sequence.sections.append(meta)
        self.queue.append(meta)

        # Move through the queue until it is emptied
        while self.queue:
            frag = self.queue.pop(0)
            if frag.addr in self.visited:
                continue
            self.visited.add(frag.addr)

            if isinstance(frag, AseqMessageFragment):
                self._parse_message_fragment(frag)
            elif isinstance(frag, AseqDataFragment):
                self._parse_data_fragment(frag)

            # If the fragment is a data fragment,
            # register it to its respective dictionary
            self._register_fragment(frag)

        return self.sequence

    def _parse_message_fragment(self, frag: AseqMessageFragment):
        """"""
        offset = frag.addr # Initial position

        # Run through the sequence data byte by byte
        # The position will be offset by the parsed message's
        # total message size (opcode + args)
        while offset < len(self.data):
            opcode = self.data[offset]
            section_type = self._infer_section(frag)
            msg_cls = AseqMessageSpec.get_message_class(section_type, opcode, self.version, frag)

            # Unknown opcode, continue to the next byte
            # Unsafe, maybe breaking would be better?
            if msg_cls is None:
                offset += 1
                continue

            # Store the message's data into its corresponding class
            msg = msg_cls.from_bytes(self.data, offset)

            # If the message sets legato or staccato,
            # change it for the entire fragment
            if isinstance(msg, (AseqChannel_Legato, AseqLayer_Legato,)):
                frag.is_legato = True
            elif isinstance(msg, (AseqChannel_Staccato, AseqLayer_Staccato,)):
                frag.is_legato = False

            frag.messages.append(msg)
            offset += msg.size # Increment position

            # Deal with pointers to other pieces of the sequence
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
                addr += 4
        if isinstance(frag, AseqFilter):
            ...
        if isinstance(frag, AseqArray):
            ...
        if isinstance(frag, AseqTable):
            ...

    def _handle_message_reference(self, frag: AseqMessageFragment, msg: AseqMessage):
        """"""
        # Pointer from metadata to a channel
        if isinstance(frag, AseqMetadata) and isinstance(msg, AseqMeta_LoadChannel):
            if frag.channels[msg.channel] is None:
                ch = Channel(msg.channel, msg.args[0].value)
                frag.channels[msg.channel] = ch
                self.queue.append(ch)

        # Pointer from channel to a note layer
        if isinstance(frag, Channel) and isinstance(msg, AseqChannel_LoadLayer):
            if frag.note_layers[msg.note_layer] is None:
                ly = NoteLayer(msg.args[0].value, is_legato=frag.is_legato)
                frag.note_layers[msg.note_layer] = ly
                self.queue.append(ly)

        # Pointer to another fragment
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

