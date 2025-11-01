from z64lib.audio.audiobank import AudiobankIndex
from z64lib.audio.audiobank.banks import InstrumentBank


class Audiobank:
    """ Represents the 'Audiobank' file in a Zelda64 ROM. """
    def __init__(self):
        self.index: AudiobankIndex = None
        self.banks: list[InstrumentBank | None] = []

    @classmethod
    def from_bytes(cls, audiobank_index: bytes | bytearray | AudiobankIndex, audiobank_data: bytes) -> 'Audiobank':
        """
        Instantiats an audiobank object using binary data.

        Args:
            audiobank_index: Binary `Audiobank`file index data from the ROM's `code` file.
            audiobank_data: Binary `Audiobank` file data.

        Returns:
            object: A fully parsed `Audiobank` file.
        """
        obj = cls()

        # Set the 'Audiobank' file's index table located in the 'code' file.
        if isinstance(audiobank_index, AudiobankIndex):
            obj.index = audiobank_index
        elif isinstance(audiobank_index, bytes | bytearray):
            obj.index = AudiobankIndex.from_bytes(audiobank_index)
        else:
            raise TypeError(f"audiobank_index must be bytes or AudiobankIndex, not {type(audiobank_index).__name__}")

        # Store entries as InstrumentBank objects
        for entry in obj.index.entries:
            if entry is None:
                obj.banks.append(None)
                continue

            bank_start = entry.rom_addr
            bank_end = bank_start + entry.bank_size
            bank_data = audiobank_data[bank_start:bank_end]

            bank = InstrumentBank.from_bytes(entry, bank_data)

            obj.banks.append(bank)

        return obj
