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
PRINT_BANK_TEST_TARGET: bool = False
WRITE_BANK: bool = False

# Audio Sequence
TEST_ASEQ: bool = False

# Cleanup
CLEAN_PYCACHE_FOLDERS: bool = True


# Ensure import works
sys.path.append(str(Path(__file__).resolve().parent.parent))
from z64lib.audiobank.bank import InstrumentBank

# Base directory of this script
BASE_DIR = Path(__file__).resolve().parent

# Paths to binary test files in "tests/"
TABLE_ENTRY: Path = BASE_DIR / "bin" / "3.bankmeta"
BANK_DATA: Path =  BASE_DIR / "bin" / "3.zbank"
AUDIO_SEQUENCE: Path = BASE_DIR / "bin" / "mm-battle.seq"

# Begin file testing
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

# Cache cleanup
if CLEAN_PYCACHE_FOLDERS:
    for pycache_dir in BASE_DIR.parent.rglob('__pycache__'):
        if pycache_dir.is_dir():
            shutil.rmtree(pycache_dir)