import struct
from dataclasses import dataclass
from z64lib.audiobank import AudiobankIndexEntry
from z64lib.audiobank.structs import Drum
from z64lib.audiobank.structs import Instrument
from z64lib.audiobank.structs import SoundEffect
from z64lib.core.allocation import MemoryAllocator


@dataclass
class BankPointer:
    address: int = 0


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
    effects: list[SoundEffect | None]
        The sound effects contained in the instrument bank.
    """
    def __init__(self):
        self.index_entry: AudiobankIndexEntry = None
        self.instruments: list[Instrument | None] = []
        self.drums: list[Drum | None] = []
        self.effects: list[SoundEffect | None] = []

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
        drum_list_addr, effect_list_addr = struct.unpack('>2I', bank_data[:0x08])

        # From this point, the from_bytes method will walk through every structure that has a pointer or data (effects)
        # and fully instantiate every required child structure. Effects are just a TunedSample struct, so the effect list
        # is just a list of TunedSample structs instead of a list of pointers to another struct. This means each entry is
        # 8 bytes long instead of 4 bytes, because that is the size of the TunedSample struct.

        # Drums
        for i in range(0, obj.index_entry.num_drums):
            addr = drum_list_addr + (i * 4)
            drum_addr = struct.unpack_from('>I', bank_data, addr)[0]
            if drum_addr != 0:
                obj.drums.append(Drum.from_bytes(bank_data, drum_addr))
            else:
                obj.drums.append(None) # Preserve null

        # Effects
        for i in range(0, obj.index_entry.num_effects):
            addr = effect_list_addr + (8 * i)
            effect = bank_data[addr:addr + 0x08]
            if effect != (b'\x00' * 8):
                obj.effects.append(SoundEffect.from_bytes(bank_data, addr))
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

    def _all_objects(self):
        """"""
        inst_objs = []
        drum_objs = []
        sample_objs = [] # Samples with books and loops
        env_objs = []

        for instrument in self.instruments:
            if instrument:
                inst_objs.append(instrument)
                envelope = getattr(instrument, 'envelope', None)
                if envelope:
                    env_objs.append(envelope)
                for attr in ['low_region_sample', 'prim_region_sample', 'high_region_sample']:
                    tuned_sample = getattr(instrument, attr, None)
                    if tuned_sample and tuned_sample.sample:
                        sample = tuned_sample.sample
                        sample_objs.append(sample)
                        sample_objs.append(sample.book)
                        sample_objs.append(sample.loop)

        for drum in self.drums:
            if drum and drum.tuned_sample:
                drum_objs.append(drum)
                envelope = getattr(drum, 'envelope', None)
                if envelope:
                    env_objs.append(envelope)
                sample = getattr(drum.tuned_sample, 'sample', None)
                if sample:
                    sample_objs.append(sample)
                    sample_objs.append(sample.book)
                    sample_objs.append(sample.loop)


        for effect in self.effects:
            if effect and effect.tuned_sample:
                sample = getattr(effect.tuned_sample, 'sample', None)
                if sample:
                    sample_objs.append(sample)
                    sample_objs.append(sample.book)
                    sample_objs.append(sample.loop)

        all_objects = sample_objs + env_objs + inst_objs + drum_objs
        return all_objects

    def _assign_addresses(self, allocator: MemoryAllocator):
        """
        Reserve memory for all instruments, drums, effects, and substructures.
        Lists are reserved after the first 0x08 bytes (header).
        """
        allocator.reserve_at(0x00, 8, data=b'\x00'*8)

        inst_list_bytes = b'\x00' * 4 * len(self.instruments)
        allocator.reserve_at(0x08, len(inst_list_bytes), data=inst_list_bytes)
        self._instrument_list = BankPointer(0x08)

        # Align to 0x80, then assign instrument, drum, sample, loop, book, and envelope addresses
        allocator.address = allocator.align_to(allocator.address, 0x10)
        for obj in self._all_objects():
            if hasattr(obj, 'size'):
                allocator.reserve_mem(obj, obj.size(), aligned=True)
            else:
                allocator.reserve_mem(obj, 0x10, aligned=True)

        if self.drums:
            drum_list_bytes = b'\x00' * 4 * len(self.drums)
            drum_list_addr = allocator.align_to(allocator.address, 0x10)
            allocator.reserve_at(drum_list_addr, len(drum_list_bytes), data=drum_list_bytes)
            self._drum_list = BankPointer(drum_list_addr)
        else:
            self._drum_list = BankPointer(0)

        if self.effects:
            effect_list_bytes = b'\x00' * 8 * len(self.effects)
            effect_list_addr = allocator.align_to(allocator.address, 0x10)
            allocator.reserve_at(effect_list_addr, len(effect_list_bytes), data=effect_list_bytes)
            self._effect_list = BankPointer(effect_list_addr)
        else:
            self._effect_list = BankPointer(0)

        inst_list_bytes = b''.join(
            struct.pack('>I', getattr(inst, 'allocated_address', 0)) if inst else b'\x00\x00\x00\x00'
            for inst in self.instruments
        )
        allocator.write(self._instrument_list.address, inst_list_bytes)

        # Properly write the drum list
        if self.drums:
            drum_list_bytes = b''.join(
                struct.pack('>I', getattr(d, 'allocated_address', 0)) if d else b'\x00\x00\x00\x00'
                for d in self.drums
            )
            allocator.write(self._drum_list.address, drum_list_bytes)

        # Properly write the effect list
        if self.effects:
            effect_list_bytes = b''.join(
                effect.to_bytes() if effect else b'\x00' * 8
                for effect in self.effects
            )
            allocator.write(self._effect_list.address, effect_list_bytes)

        header_bytes = struct.pack('>2I', self._drum_list.address, self._effect_list.address)
        allocator.write(0x00, header_bytes)

    def to_bytes(self, truncate_index_entry: bool = False) -> tuple[bytes, bytes]:
        """"""
        allocator = MemoryAllocator()
        self._assign_addresses(allocator)

        bank_bytes = allocator.assemble(auto_patch_pointer=True)

        index_bytes = self.index_entry.to_bytes()
        if truncate_index_entry:
            index_bytes = index_bytes[-8:]

        return (index_bytes, bank_bytes)

    def __repr__(self):
        lines = [f"{type(self).__name__}("]

        lines.append(f"  index_entry={repr(self.index_entry).replace('\n', '\n    ')}")

        def format_list(name, items):
            if not items:
                return f"  {name}=[]"
            lines_list = []
            for item in items:
                if item is None:
                    lines_list.append("None")
                else:
                    lines_list.append(repr(item).replace('\n', '\n    '))
            return f"  {name}=[\n    " + ',\n    '.join(lines_list) + "\n  ]"

        lines.append(format_list('instruments', self.instruments))
        lines.append(format_list('drums', self.drums))
        lines.append(format_list('effects', self.effects))

        lines.append(")")
        return '\n'.join(lines)
