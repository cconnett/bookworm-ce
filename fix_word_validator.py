import struct
import sys

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} infile outfile")
    sys.exit(2)

rom = bytearray(open(sys.argv[1], "rb").read())
initial_size = len(rom)
# Remove shuffle suggestion nag box.
rom[0x7844:0x7848] = b"\x1e\xff\x2f\xe1"  # bx lr

# Hotfix for missing check in ValidateWordImpl.
rom[0x12C94:0x12CA0] = (
    b"\x40\x00\x11\xe2"  # ands r0, r1, #0x40
    b"\xf6\xff\xff\x0a"  # beq ValidateWordReturn
    b"\xd3\x74\x0f\xea"  # b 0x083EFFF0
)
rom[0x3EFFF0:0x3F0000] = (
    b"\x06\xcc\xa0\xe1"  # mov r12, r1, lsr #6
    b"\x4c\x3c\xa0\xe1"  # and r0, 12, #1
    b"\x03\x00\x53\xe3"  # cmp r0, #0
    b"\x27\x8b\xf0\xea"  # b ValidateWordReturn
)

new_letter_frequency_table = [
    7578,
    2327,
    3707,
    3872,
    10841,
    1655,
    2971,
    2561,
    7473,
    559,
    1543,
    5265,
    2937,
    5796,
    6069,
    3021,
    482,
    6763,
    5080,
    5734,
    3399,
    1198,
    1324,
    633,
    1948,
    764,
]
# Apply new letter frequency table.
LETTER_FREQ_TABLE_ADDR = 0xF7498
rom[LETTER_FREQ_TABLE_ADDR : LETTER_FREQ_TABLE_ADDR + 26 * 4] = struct.pack(
    "<26I", *new_letter_frequency_table
)

assert len(rom) == initial_size, "ROM size changed!"
open(sys.argv[2], "wb").write(rom)
