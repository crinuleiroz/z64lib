import struct
from dataclasses import dataclass

from z64lib.core.allocation import MemoryAllocator
from z64lib.core.alignment import align_to
from z64lib.audio.audiobank import AudiobankIndexEntry
from z64lib.audio.audiobank.bank.structs import Instrument
from z64lib.audio.audiobank.bank.structs import Drum
from z64lib.audio.audiobank.bank.structs import TunedSample


@dataclass
class BankPointer:
    addr: int = 0


class InstrumentBank:
    """
    Represents a Zelda64 instrument bank.

    Attributes
    ----------
    index_entry: AudiobankIndexEntry
        The instrument bank's corresponding entry from the `code` file's audiobank index.
    instruments: list[Instrument | None]
        The instruments contained in the instrument bank.
    drums: list[Drum | None]
        The drums contained in the instrument bank.
    effects: list[TunedSample | None]
        The sound effects contained in the instrument bank.
    """
    def __init__(self):
        self.index_entry: AudiobankIndexEntry = None
        self.instruments: list[Instrument | None] = []
        self.drums: list[Drum | None] = []
        self.effects: list[TunedSample | None] = []

        self.drum_list_addr: int = 0
        self.effect_list_addr: int = 0

        # Private registries for compiling to binary
        self._instrument_registry = {}
        self._drum_registry = {}
        self._effect_registry = {}
        self._sample_registry = {}
        self._envelope_registry = {}
        self._loopbook_registry = {}
        self._codebook_registry = {}

    @classmethod
    def from_bytes(cls, index_entry: bytes | bytearray | AudiobankIndexEntry, bank_data: bytes | bytearray) -> 'InstrumentBank':
        """
        Instantiates an `InstrumentBank` object from binary data.

        Parameters
        ----------
        index_entry: bytes | bytearray | AudiobankIndexEntry
            `Audiobank` file index entry data taken from the ROM's `code` file.
        bank_data: bytes | bytearray
            Binary instrument bank data.

        Returns
        ----------
        InstrumentBank
            Returns a fully instantiated `InstrumentBank` object.

        Raises
        ----------
        TypeError
            Invalid `index_entry` type.
        """
        obj = cls()

        if isinstance(index_entry, AudiobankIndexEntry):
            obj.index_entry = index_entry
        elif isinstance(index_entry, (bytes, bytearray)):
            obj.index_entry = AudiobankIndexEntry.from_bytes(index_entry)
        else:
            raise TypeError(f"index_entry must be bytes or AudiobankIndexEntry, not {type(index_entry).__name__}")

        # Extract the offsets for the drum list and effect list
        obj.drum_list_addr, obj.effect_list_addr = struct.unpack('>2I', bank_data[:0x08])

        # From this point, the from_bytes method will walk through every structure that has a pointer or data (effects)
        # and fully instantiate every required child structure. Effects are just a TunedSample struct, so the effect list
        # is just a list of TunedSample structs instead of a list of pointers to another struct. This means each entry is
        # 8 bytes long instead of 4 bytes, because that is the size of the TunedSample struct.

        # Drums
        for i in range(0, obj.index_entry.num_drums):
            addr = obj.drum_list_addr + (i * 4)
            drum_addr = struct.unpack_from('>I', bank_data, addr)[0]
            if drum_addr != 0:
                obj.drums.append(Drum.from_bytes(bank_data, drum_addr))
            else:
                obj.drums.append(None) # Preserve null

        # Effects
        for i in range(0, obj.index_entry.num_effects):
            addr = obj.effect_list_addr + (8 * i)
            effect = bank_data[addr:addr + 0x08]
            if effect != (b'\x00' * 8):
                obj.effects.append(TunedSample.from_bytes(bank_data, addr))
            else:
                obj.effects.append(None) # Preserve null

        # Instruments
        for i in range(0, obj.index_entry.num_instruments):
            addr = 0x08 + (i * 4)
            instrument_addr = struct.unpack_from('>I', bank_data, addr)[0]
            if instrument_addr != 0:
                obj.instruments.append(Instrument.from_bytes(bank_data, instrument_addr))
            else:
                obj.instruments.append(None) # Preserve null

        return obj

    def _add_to_registry(self, item, hash, registry):
        if hash not in registry:
            registry[hash] = item

    def _register_envelope_data(self, envelope):
        if envelope is None:
            return

        self._add_to_registry(envelope, envelope.get_hash(), self._envelope_registry)

    def _register_sample_data(self, sample):
        if sample is None:
            return

        loopbook = sample.loop
        codebook = sample.book

        self._add_to_registry(sample, sample.get_hash(), self._sample_registry)
        self._add_to_registry(loopbook, loopbook.get_hash(), self._loopbook_registry)
        self._add_to_registry(codebook, codebook.get_hash(), self._codebook_registry)

    def _process_instrument(self, instrument):
        if instrument is None:
            return

        self._add_to_registry(instrument, instrument.get_hash(), self._instrument_registry)
        self._register_envelope_data(instrument.envelope)
        for attr in ['low_region_sample', 'prim_region_sample', 'high_region_sample']:
            tuned_sample = getattr(instrument, attr)
            if tuned_sample:
                self._register_sample_data(tuned_sample.sample)

    def _process_drum(self, drum):
        if drum is None:
            return

        self._add_to_registry(drum, drum.get_hash(), self._drum_registry)
        self._register_sample_data(drum.tuned_sample.sample)
        self._register_envelope_data(drum.envelope)

    def _process_effect(self, effect):
        if effect is None:
            return

        self._add_to_registry(effect, effect.get_hash(), self._effect_registry)
        if effect.sample:
            self._register_sample_data(effect.sample)

    def _reassign_registry_refs(self):
        # Update sample references
        for sample in self._sample_registry.values():
            sample.loop = self._loopbook_registry[sample.loop.get_hash()]
            sample.book = self._codebook_registry[sample.book.get_hash()]

        # Update instrument references
        for instrument in self._instrument_registry.values():
            instrument.envelope = self._envelope_registry[instrument.envelope.get_hash()]

            for attr in ['low_region_sample', 'prim_region_sample', 'high_region_sample']:
                tuned_sample = getattr(instrument, attr)
                if tuned_sample and tuned_sample.sample:
                    sample = self._sample_registry[tuned_sample.sample.get_hash()]
                    tuned_sample.sample = sample

        # Update drum references
        for drum in self._drum_registry.values():
            drum.envelope = self._envelope_registry[drum.envelope.get_hash()]
            if drum.tuned_sample and drum.tuned_sample.sample:
                drum.tuned_sample.sample = self._sample_registry[drum.tuned_sample.sample.get_hash()]

        # Update effect references
        for effect in self._effect_registry.values():
            if effect and effect.sample:
                effect.sample = self._sample_registry[effect.sample.get_hash()]

    def _assign_addresses(self, allocator: MemoryAllocator):
        # DO NOT CHANGE ORDER OF ITEMS HERE

        # Instrument List
        # The position of the instrument list is fixed after the first two
        # pointers (drum list and effect list pointers).
        self._instrument_list = BankPointer()
        self._instrument_list.addr = 0x00000008

        # Drum List
        # The position of the drum list can be anywhere in the bank, here
        # it is placed right after the instrument list.
        self._drum_list = BankPointer()
        if len(self.drums) > 0:
            self._drum_list.addr = align_to(self._instrument_list.addr + (len(self.instruments) * 4), 0x10)
        else:
            self._drum_list.addr = 0

        # Effect List
        # The position of the effect list can be anywhere in the bank, here
        # it is placed right after the drum list.
        self._effect_list = BankPointer()
        if len(self.effects) > 0:
            self._effect_list.addr = align_to(self._drum_list.addr + (len(self.drums) * 4), 0x10)

        # Calulate data address
        allocator.addr = align_to(
            max(
                self._instrument_list.addr + (len(self.instruments) * 4),
                self._drum_list.addr + (len(self.drums) * 4) if self._drum_list.addr > 0 else 0,
                self._effect_list.addr + (len(self.effects) * 8) if self._effect_list.addr > 0 else 0,
            ),
            0x10
        )

        # The order of items here can be changed, it will change the final
        # structure of the bank, but the data will be where it needs to be.
        #
        # Original order:
        #       Instruments -> Drums -> Samples -> Loops -> Books -> Envelopes
        for instrument in self._instrument_registry.values():
            allocator.reserve_mem(instrument, 0x20, aligned=True)

        for drum in self._drum_registry.values():
            allocator.reserve_mem(drum, 0x10, aligned=True)

        for sample in self._sample_registry.values():
            allocator.reserve_mem(sample, 0x10, aligned=True)

        for loopbook in self._loopbook_registry.values():
            allocator.reserve_mem(loopbook, loopbook.size(), aligned=True)

        for codebook in self._codebook_registry.values():
            allocator.reserve_mem(codebook, codebook.size(), aligned=True)

        for envelope in self._envelope_registry.values():
            allocator.reserve_mem(envelope, envelope.size(), aligned=True)

    def to_bytes(self, truncate_index_entry: bool = False) -> tuple[bytes, bytes]:
        """
        Compiles an `InstrumentBank` object from memory to binary.

        Returns
        ----------
        tuple[bytes, bytes]
            A tuple containing the bank's index entry and binary data.
        """

        # Reference deduplication
        # ————————————————————————————————————————————————————————————————
        # If duplicate data exists in the bank, then the data should be
        # replaced with already known existing data
        for instrument in self.instruments:
            self._process_instrument(instrument)

        for drum in self.drums:
            self._process_drum(drum)

        for effect in self.effects:
            self._process_effect(effect)

        self.instruments = [
            self._instrument_registry[instrument.get_hash()] if instrument else None
            for instrument in self.instruments
        ]
        self.drums = [
            self._drum_registry[drum.get_hash()] if drum else None
            for drum in self.drums
        ]
        self.effects = [
            self._effect_registry[effect.get_hash()] if effect else None
            for effect in self.effects
        ]
        self._reassign_registry_refs()

        # Pointer allocation
        allocator = MemoryAllocator()
        self._assign_addresses(allocator)

        # Create the buffer
        buffer = bytearray(align_to(allocator.addr, 0x10))

        # Write drum list and effect list pointers
        struct.pack_into('>2I', buffer, 0x00,
                         self._drum_list.addr,
                         self._effect_list.addr)

        # Write pointer lists
        for i, instrument in enumerate(self.instruments):
            struct.pack_into('>I', buffer, self._instrument_list.addr + (i * 4),
                             instrument._address if instrument else 0) # _address is assigned in MemoryAllocator.reserve_mem()

        for i, drum in enumerate(self.drums):
            struct.pack_into('>I', buffer, self._drum_list.addr + (i * 4),
                             drum._address if drum else 0) # _address is assigned in MemoryAllocator.reserve_mem()

        for i, effect in enumerate(self.effects):
            if effect is None:
                continue
            start = self._effect_list.addr + (i * 8)
            buffer[start:start + 8] = effect.to_bytes()

        # Write structs
        for addr, obj in sorted(allocator.entries, key=lambda x: x[0]):
            if obj is None:
                continue
            elif isinstance(obj, BankPointer):
                continue

            data = obj.to_bytes()
            buffer[addr:addr + len(data)] = data

        if truncate_index_entry:
            return (self.index_entry.to_bytes()[-8:], bytes(buffer))
        else:
            return (self.index_entry.to_bytes()[-8:], bytes(buffer))

    def write_bytes(self, file_name: str, file_path: str, output_metadata: bool = True, truncate_metadata: bool = False, output_bank: bool = True):
        """
        Compiles an `InstrumentBank` object from memory to binary, then writes the output to a file.
        """
        from pathlib import Path

        out_path = Path(file_path)
        bankmeta_bytes, bank_bytes = self.to_bytes(truncate_index_entry=truncate_metadata)

        if output_metadata:
            (out_path / f'{file_name}.bankmeta').write_bytes(bankmeta_bytes)
        if output_bank:
            (out_path / f'{file_name}.zbank').write_bytes(bank_bytes)

    def __repr__(self):
        lines = [f'{type(self).__name__}(']

        lines.append(f'  index_entry={repr(self.index_entry).replace('\n', '\n    ')}')

        def format_list(name, items):
            if not items:
                return f'  {name}=[]'
            lines_list = []
            for item in items:
                if item is None:
                    lines_list.append('None')
                else:
                    lines_list.append(repr(item).replace('\n', '\n    '))
            return f'  {name}=[\n    ' + ',\n    '.join(lines_list) + '\n  ]'

        lines.append(format_list('instruments', self.instruments))
        lines.append(format_list('drums', self.drums))
        lines.append(format_list('effects', self.effects))

        lines.append(')')
        return '\n'.join(lines)
