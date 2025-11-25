import sys
import shutil
from pathlib import Path
from helpers import open_read

# Ensure import works
sys.path.append(str(Path(__file__).resolve().parent.parent))

# ============== #
#  TEST OPTIONS  #
# ============== #

# Types
TEST_TYPES: bool = True

# Instrument Bank
TEST_BANK: bool = False
BANK_TEST_TARGET: str = "instrument" # "instrument" / "drum" / "effect"
PRINT_BANK_TEST_TARGET: bool = True
WRITE_BANK: bool = False

# Audio Sequence
TEST_ASEQ: bool = False

# Extras
TEST_EXTRAS: bool = False

# Cleanup
CLEAN_PYCACHE_FOLDERS: bool = True

# Base directory of this script
BASE_DIR = Path(__file__).resolve().parent

# Paths to binary test files in "tests/"
TABLE_ENTRY: Path = BASE_DIR / "bin" / "3.bankmeta"
BANK_DATA: Path =  BASE_DIR / "bin" / "3.zbank"
AUDIO_SEQUENCE: Path = BASE_DIR / "bin" / "mm-battle.seq"
MUSIC_METADATA_FILE: Path = BASE_DIR / "music" / "test_metadata.mmrs"
OOTRS_FILE: Path = BASE_DIR / "music" / "test_ootrs.ootrs"
MMRS_FILE: Path = BASE_DIR / "music" / "test_mmrs.mmrs"

# =========== #
#  TEST DATA  #
# =========== #

# Type testing
if TEST_TYPES:
    from z64lib.types import *

    print(f'value={s16(0xFFFF)}', f'min={s16.MIN}', f'max={s16.MAX}, bytes={s16.to_bytes(0xFFFF)}')


# Audiobank Testing
if TEST_BANK:
    from z64lib.audiobank import InstrumentBank

    entry_data = open_read(TABLE_ENTRY, mode='rb')
    bank_data = open_read(BANK_DATA, mode='rb')

    # Create the bank
    bank = InstrumentBank.from_bytes(entry_data, bank_data)

    if PRINT_BANK_TEST_TARGET:
        # Test target selection
        match BANK_TEST_TARGET.lower():
            case "instrument":
                items = bank.instruments
            case "drum":
                items = bank.drums
            case "effect":
                items = bank.effects
            case _:
                items = None

        # Test __repr__ and to_bytes()
        if items and items[0]:
            print(f"Testing {BANK_TEST_TARGET} '__repr__':")
            print(items[0])
            print(f"Testing {BANK_TEST_TARGET} 'to_bytes()':")
            print(items[0].to_bytes().hex())
        else:
            print(f"No {BANK_TEST_TARGET}s found in bank")

    if WRITE_BANK:
        print(f"Writing index entry and bank data to file...")
        bank.write_bytes('test_bank', BASE_DIR, truncate_metadata=True)


# Audioseq Testing
if TEST_ASEQ:
    from z64lib.audioseq import AseqParser
    from z64lib.core.enums import AseqVersion
    from z64lib.audioseq.messages import AseqLayer_NoteDVG, AseqLayer_NoteDV, AseqLayer_NoteVG

    aseq_data = open_read(AUDIO_SEQUENCE, mode='rb')
    parser = AseqParser(aseq_data, AseqVersion.OOT)
    seq = parser.parse()

    seq_meta = seq.sections[0]
    seq_ch_0 = seq_meta.get_channel(0)
    seq_ch_1 = seq_meta.get_channel(1)
    seq_ch_3 = seq_meta.get_channel(3)
    seq_ch_5 = seq_meta.get_channel(5)
    seq_ch_7 = seq_meta.get_channel(7)
    seq_ch_9 = seq_meta.get_channel(9)
    seq_ch_10 = seq_meta.get_channel(10)
    seq_ch_11 = seq_meta.get_channel(11)
    seq_ch_13 = seq_meta.get_channel(13)
    seq_ch_15 = seq_meta.get_channel(15)

    # for msg in seq_meta.messages:
    #     print(msg)
    for msg in seq_ch_0.get_layer(0).messages:
        if isinstance(msg, AseqLayer_NoteDVG):
            print(msg.midi_note)
        elif isinstance(msg, AseqLayer_NoteDV):
            print(msg.midi_note)
        elif isinstance(msg, AseqLayer_NoteVG):
            print(msg.midi_note)
        else:
            print(msg)


# Extras testing
if TEST_EXTRAS:
    from z64lib.extras.randomizers.music import MusicFile

    # Music file with .metadata
    # mf_metadata = MusicFile.from_zip(MUSIC_METADATA_FILE)
    # print(mf_metadata.metadata)

    # OOTRS file with .meta
    mf_ootrs = MusicFile.from_zip(OOTRS_FILE)
    print(mf_ootrs.metadata)

    # MMRS file with categories.txt
    # mf_mmrs = MusicFile.from_zip(MMRS_FILE)
    # print(mf_mmrs.metadata)

# ============== #
#  TEST CLEANUP  #
# ============== #

# Cache cleanup
if CLEAN_PYCACHE_FOLDERS:
    for pycache_dir in BASE_DIR.parent.rglob('__pycache__'):
        if pycache_dir.is_dir():
            shutil.rmtree(pycache_dir)