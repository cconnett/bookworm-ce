import pprint
import struct
import sys

if len(sys.argv) != 4:
    print(f"Usage: sys.argv[0] infile outfile lexicon.bwtrie")
    sys.exit(2)

rom = bytearray(open(sys.argv[1], "rb").read())

LEXICON_ADDRESS = 0xF7C38
LEXICON_DEFAULT_BOUNDARY = 0x14FFA0
LEXICON_EXPANSION_ADDRESS = 0x3DBEB4
LEXICON_EXPANSION_BOUNDARY = 0x3DFFF0

trie = open(sys.argv[3], "rb").read()
# Assume all 26 letters are present in the top level.
section_starts = {
    chr(ord("A") + (letter & 0x1F)): (i + 1) * 4 + (jump_hi << 16) + jump_lo
    for i, (letter, jump_lo, jump_hi) in enumerate(
        struct.iter_unpack("<BHB", trie[: 26 * 4])
    )
}
section_ranges = {
    letter: (section_starts[letter], section_starts[chr(ord(letter) + 1)])
    for letter in list(section_starts.keys())[:-1]
}
section_ranges["Z"] = (section_starts["Z"], len(trie))


segment_address = LEXICON_ADDRESS + 4 * 26
boundary_address = LEXICON_DEFAULT_BOUNDARY
in_expansion = False
for i, (letter, (start, end)) in enumerate(section_ranges.items()):
    segment = trie[start:end]
    if segment_address + len(segment) > boundary_address:
        if in_expansion:
            raise ValueError("Out of space")
        in_expansion = True
        print("--- Jumped to expansion ---")
        segment_address = LEXICON_EXPANSION_ADDRESS
        boundary_address = LEXICON_EXPANSION_BOUNDARY
    rom[segment_address : segment_address + len(segment)] = segment
    level_0_jump_base = LEXICON_ADDRESS + (i + 1) * 4
    level_0_jump_address = LEXICON_ADDRESS + i * 4 + 1
    new_jump = segment_address - level_0_jump_base
    new_jump_bytes = struct.pack("<I", new_jump)
    if new_jump_bytes[3] != 0:
        raise ValueError("jump size overflow")
    new_jump_bytes = new_jump_bytes[:3]
    rom[level_0_jump_address : level_0_jump_address + 3] = new_jump_bytes
    print(
        f"Wrote {letter} segment to {hex(segment_address)}. "
        f"{new_jump=} ({new_jump:06x})"
    )
    segment_address += len(segment)


print(hex(len(rom)))
open(sys.argv[2], "wb").write(rom)
