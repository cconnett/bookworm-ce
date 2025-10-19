import sys

RETURN = b"\x1e\xff\x2f\xe1"  # bx lr

if len(sys.argv) != 3:
    print(f"Usage: sys.argv[0] infile outfile")
    sys.exit(2)

rom = bytearray(open(sys.argv[1], "rb").read())
initial_size = len(rom)
# Remove shuffle suggestion nag box.
rom[0x7844:0x7848] = RETURN

# Hotfix for missing check in ValidateWordImpl.
rom[0x12C94:0x12CA0] = b"\x40\x00\x11\xe2" b"\xf6\xff\xff\x0a" b"\xd3\x34\x0f\xea"
rom[0x3DFFF0:0x3E0000] = (
    b"\x06\xcc\xa0\xe1" b"\x4c\x3c\xa0\xe1" b"\x03\x00\x53\xe3" b"\x27\xcb\xf0\xea"
)

assert len(rom) == initial_size, "ROM size changed!"
open(sys.argv[2], "wb").write(rom)
