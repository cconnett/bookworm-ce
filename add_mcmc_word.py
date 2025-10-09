import struct
import sys

if len(sys.argv) != 4:
    print(f"Usage: sys.argv[0] infile outfile pick_word_arm.o")
    sys.exit(2)
pass

rom = bytearray(open(sys.argv[1], "rb").read())

# Read from pick_word.o
libpick_word = open(sys.argv[3], "rb").read()
rodata = libpick_word[0x2A8 : 0x2A8 + 0x6C]
text_offset = 0x34
random_word = libpick_word[text_offset : text_offset + 0x1D0]
mcmc_word = libpick_word[text_offset + 0x1D0 : text_offset + 0x1D0 + 0xA4]

# Put compiled functions into the rom at base address TARGET_BASE
TARGET_BASE = 0x3E0000
GBA_ROM_DOMAIN = 0x08000000
TEXT_SECTION = TARGET_BASE + len(rodata)
progress = 0

for obj in [rodata, random_word, mcmc_word]:
    rom[TARGET_BASE + progress : TARGET_BASE + progress + len(obj)] = obj
    progress += len(obj)

# Go through relocation table and link things
rom[TEXT_SECTION + 0x1CC : TEXT_SECTION + 0x1CC + 4] = struct.pack(
    "<I", GBA_ROM_DOMAIN + TARGET_BASE
)
rom[TEXT_SECTION + 0x1EC] = 0x83
rom[TEXT_SECTION + 0x200] = 0x7E

# Edit original pick_bonus_word function to call our new function.
rom[0x5988:0x5998] = struct.pack(
    "<IIII", 0xE1A00005, 0xE1A01004, 0xE1A00000, 0xEB0F6A28
)

print(hex(len(rom)))
open(sys.argv[2], "wb").write(rom)
