import sys
import shutil
from pathlib import Path
from helpers import open_read

# ============== #
#  TEST OPTIONS  #
# ============== #

# Instrument Bank
TEST_BANK: bool = False
BANK_TEST_TARGET: str = "instrument" # or "drum" / "effect"
PRINT_BANK_TEST_TARGET: bool = True
WRITE_BANK: bool = True

# Audio Sequence
TEST_ASEQ: bool = True

# Cleanup
CLEAN_PYCACHE_FOLDERS: bool = True


# Ensure import works
sys.path.append(str(Path(__file__).resolve().parent.parent))
from z64lib.audiobank.bank import InstrumentBank
from z64lib.audioseq import AseqParser
from z64lib.core.enums import AseqVersion


# Base directory of this script
BASE_DIR = Path(__file__).resolve().parent

# Paths to binary test files in "tests/"
TABLE_ENTRY: Path = BASE_DIR / "bin" / "3.bankmeta"
BANK_DATA: Path =  BASE_DIR / "bin" / "3.zbank"
AUDIO_SEQUENCE: Path = BASE_DIR / "bin" / "mm-battle.seq"

# =========== #
#  TEST DATA  #
# =========== #

# Audiobank Testing
if TEST_BANK:
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

    for msg in seq_meta.messages:
        print(msg)
    # for msg in seq_ch_0.get_layer(0).messages:
    #     print(msg)

# ============== #
#  TEST CLEANUP  #
# ============== #

# Cache cleanup
if CLEAN_PYCACHE_FOLDERS:
    for pycache_dir in BASE_DIR.parent.rglob('__pycache__'):
        if pycache_dir.is_dir():
            shutil.rmtree(pycache_dir)