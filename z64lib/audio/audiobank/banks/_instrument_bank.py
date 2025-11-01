import struct

from z64lib.audio.audiobank import AudiobankIndexEntry
from z64lib.audio.audiobank.banks.structures import Instrument
from z64lib.audio.audiobank.banks.structures import Drum
from z64lib.audio.audiobank.banks.structures import TunedSample


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

        # Public, but
        self.drum_list_offset: int = 0
        self.effect_list_offset: int = 0

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
        obj.drum_list_offset, obj.effect_list_offset = struct.unpack('>2I', bank_data[:0x08])

        # From this point, the from_bytes method will walk through every structure that has a pointer or data (effects)
        # and fully instantiate every required child structure. Effects are just a TunedSample struct, so the effect list
        # is just a list of TunedSample structs instead of a list of pointers to another struct. This means each entry is
        # 8 bytes long instead of 4 bytes, because that is the size of the TunedSample struct.

        # Drums
        for i in range(0, obj.index_entry.num_drums):
            offset = obj.drum_list_offset + (i * 4)
            drum_offset = struct.unpack_from('>I', bank_data, offset)[0]
            if drum_offset != 0:
                obj.drums.append(Drum.from_bytes(bank_data, drum_offset))
            else:
                obj.drums.append(None) # Preserve null

        # Effects
        for i in range(0, obj.index_entry.num_effects):
            offset = obj.effect_list_offset + (8 * i)
            effect = bank_data[offset:offset + 0x08]
            if effect != (b'\x00' * 8):
                obj.effects.append(TunedSample.from_bytes(bank_data, offset))
            else:
                obj.effects.append(None) # Preserve null

        # Instruments
        for i in range(0, obj.index_entry.num_instruments):
            offset = 0x08 + (i * 4)
            instrument_offset = struct.unpack_from('>I', bank_data, offset)[0]
            if instrument_offset != 0:
                obj.instruments.append(Instrument.from_bytes(bank_data, instrument_offset))
            else:
                obj.instruments.append(None) # Preserve null

        return obj

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
