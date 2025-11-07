import sys
from pathlib import Path

# Ensure import works
sys.path.append(str(Path(__file__).resolve().parent.parent))
from z64lib.audio.audiobank.bank import InstrumentBank

# Base directory of this script
BASE_DIR = Path(__file__).resolve().parent

# Paths to banks folder insides "tests/"
TABLE_ENTRY: Path = BASE_DIR / "bin" / "3.bankmeta"
BANK_DATA: Path =  BASE_DIR / "bin" / "3.zbank"

# Begin file testing
with open(TABLE_ENTRY, 'rb') as e:
    entry_data = e.read()

with open(BANK_DATA, 'rb') as b:
    bank_data = b.read()

# Test print
bank = InstrumentBank.from_bytes(entry_data, bank_data)
print(bank.instruments[0])

bytes = bank.instruments[0].to_bytes()
print(bytes.hex())