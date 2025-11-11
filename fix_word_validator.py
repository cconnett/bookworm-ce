import struct
import sys

RETURN = b"\x1e\xff\x2f\xe1"  # bx lr

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} infile outfile")
    sys.exit(2)

rom = bytearray(open(sys.argv[1], "rb").read())
initial_size = len(rom)
# Remove shuffle suggestion nag box.
rom[0x7844:0x7848] = RETURN

# Hotfix for missing check in ValidateWordImpl.
rom[0x12C94:0x12CA0] = b"\x40\x00\x11\xe2" b"\xf6\xff\xff\x0a" b"\xd3\x74\x0f\xea"
rom[0x3EFFF0:0x3F0000] = (
    b"\x06\xcc\xa0\xe1" b"\x4c\x3c\xa0\xe1" b"\x03\x00\x53\xe3" b"\x27\x8b\xf0\xea"
)

new_letter_frequency_table = [
    7966,
    2193,
    3711,
    3891,
    11554,
    1455,
    2901,
    2450,
    7851,
    249,
    1331,
    5423,
    2864,
    6008,
    6307,
    2956,
    165,
    7071,
    5220,
    5939,
    3371,
    952,
    1091,
    331,
    1776,
    474,
]

LETTER_FREQ_TABLE_ADDR = 0xF7498
rom[LETTER_FREQ_TABLE_ADDR : LETTER_FREQ_TABLE_ADDR + 26 * 4] = struct.pack(
    "<26I", *new_letter_frequency_table
)


assert len(rom) == initial_size, "ROM size changed!"
open(sys.argv[2], "wb").write(rom)
