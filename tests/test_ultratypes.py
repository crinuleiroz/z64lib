import sys
import shutil
from pathlib import Path


# Ensure import works
sys.path.append(str(Path(__file__).resolve().parent.parent))

# ============== #
#  TEST OPTIONS  #
# ============== #

# Types
TEST_PRIMITIVES: bool = False
TEST_BITFIELDS: bool = False
TEST_UNIONS: bool = False
TEST_ARRAYS: bool = False
TEST_STRUCTS: bool = True
TEST_POINTERS: bool = False

# Cleanup
CLEAN_PYCACHE_FOLDERS: bool = True

# Base directory of this script
BASE_DIR = Path(__file__).resolve().parent

# =========== #
#   HELPERS   #
# =========== #

def printb(buf: bytes | bytearray) -> str:
    """ Print a bytes-like object without ASCII characters. """
    print(''.join(f'\\x{b:02x}' for b in buf))

# =========== #
#  TEST DATA  #
# =========== #

if TEST_PRIMITIVES:
    from z64lib.ultratypes.primitives import *
    char_buffer = b'\xFF'
    short_buffer = b'\xFF\xFF'
    long_buffer = b'\xFF\xFF\xFF\xFF'
    longlong_buffer = b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'

    uint8_t = u8.from_bytes(char_buffer, 0)
    int8_t = s8.from_bytes(char_buffer, 0)
    uint16_t = u16.from_bytes(short_buffer, 0)
    int16_t = s16.from_bytes(short_buffer, 0)
    uint32_t = u32.from_bytes(long_buffer, 0)
    int32_t = s32.from_bytes(long_buffer, 0)
    uint64_t = u64.from_bytes(longlong_buffer, 0)
    int64_t = s64.from_bytes(longlong_buffer, 0)

    print(uint8_t, uint8_t.buffer, uint8_t.view)
    print(int8_t, int8_t.buffer, int8_t.view)
    print(uint16_t, uint16_t.buffer, uint16_t.view)
    print(int16_t, int16_t.buffer, int16_t.view)
    print(uint32_t, uint32_t.buffer, uint32_t.view)
    print(int32_t, int32_t.buffer, int32_t.view)
    print(uint64_t, uint64_t.buffer, uint64_t.view)
    print(int64_t, int64_t.buffer, int64_t.view)

if TEST_STRUCTS:
    from z64lib.core.enums import AudioSampleCodec, AudioStorageMedium
    from z64lib.ultratypes.primitives import *
    from z64lib.ultratypes.composites import *

    struct_buffer = bytearray(b'\xFF\x02\x00\x46\x86\xFF\xFF\xFF')

    class NestedStruct(structure):
        _members_ = [
            ('uint24', u24),
        ]

    class TestStruct(structure):
        _members_ = [
            ('uint8', u8),
            ('bitfield', bitfield[u32, [
                ('codec', 4),
                ('medium', 2),
                ('is_cached', 1),
                ('is_relocated', 1),
                ('size', 24),
            ]]),
            ('uni', union[3, [
                ('uint8', u8),
                ('uint24', u24),
            ]]),
        ]
        _attributes_ = {
            'align': 0x10,
            'pack': 1,
        }
        _bools_ = {
            'is_cached',
            'is_relocated'
        }
        _enums_ = {
            'codec': AudioSampleCodec,
            'medium': AudioStorageMedium
        }

    arr = array[u16]
    # a = arr()
    # print(a.buffer)

    U = union[1, [('u8', u8)]]
    u = U()
    print(u.buffer)

    test_struct = TestStruct.from_bytes(struct_buffer, 0)
    print(
        f"{test_struct}\n"
        f"{test_struct.buffer}"
    )

    print(test_struct.codec)
    test_struct.codec = AudioSampleCodec.SMALL_ADPCM
    print(test_struct.codec)
    printb(test_struct.buffer)

# ============== #
#  TEST CLEANUP  #
# ============== #

# Cache cleanup
if CLEAN_PYCACHE_FOLDERS:
    for pycache_dir in BASE_DIR.parent.rglob('__pycache__'):
        if pycache_dir.is_dir():
            shutil.rmtree(pycache_dir)