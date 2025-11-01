import struct

from z64lib.audio.audiobank import AudiobankIndexEntry


class AudiobankIndex:
    """ Represents an index of audiobank entries. """
    def __init__(self):
        self.num_entries: int = 0
        self.entries: list[AudiobankIndexEntry | None] = []

    @classmethod
    def from_bytes(cls, audiobank_index: bytes | bytearray) -> 'AudiobankIndex':
        """
        Instantiates an audiobank index object using binary data.

        Args:
            audiobank_index: Binary `Audiobank` index data.

        Returns:
            object: A fully instantiated `Audiobank` index.
        """
        obj = cls()

        # Extract the number of entries from the table's first 2 bytes
        obj.num_entries = struct.unpack('>H', audiobank_index[0:2])[0]

        # Split the entries from the full table
        entries = audiobank_index[0x10:]

        # Store entries as AudiobankIndexEntry objects
        for i in range(0, obj.num_entries):
            start = i * 0x10
            end = start + 0x10
            entry_data = entries[start:end]

            entry = AudiobankIndexEntry.from_bytes(entry_data)

            # Treat null entries as None
            if entry.rom_addr == 0:
                obj.entries.append(None)
            else:
                obj.entries.append(entry)

        return obj