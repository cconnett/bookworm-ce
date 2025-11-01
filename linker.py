import struct
import subprocess
import sys

if len(sys.argv) != 4:
    print(f"Usage: sys.argv[0] infile outfile code.o")
    sys.exit(2)
pass

rom = bytearray(open(sys.argv[1], "rb").read())

# 0. Read from object file
libpick_word = open(sys.argv[3], "rb").read()


def run_readelf(mode):
    proc = subprocess.run(
        ["arm-none-eabi-readelf", f"-{mode}", sys.argv[3]],
        capture_output=True,
        encoding="utf-8",
    )
    proc.check_returncode()
    return proc.stdout.split("\n")


section_headers = run_readelf("S")[4:]
relocation_entries = run_readelf("r")[5:]
symbol_table = run_readelf("s")[5:]

sections = {
    name: (int(offset, base=16), int(size, base=16))
    for name, type_, addr, offset, size, _ in (
        line[7:].split(maxsplit=5) for line in section_headers if line.startswith("  [")
    )
}

relocation_entries = [
    (int(offset, base=16), type_, int(value), name)
    for offset, info, type_, value, name in (
        line.split() for line in relocation_entries if len(line.split()) == 5
    )
]

symbols = {
    name: (int(value, base=16), int(size), type_)
    for (num, value, size, type_, _, _, _, name) in (
        line.split() for line in symbol_table if len(line.split()) == 8
    )
}


GBA_ROM_DOMAIN = 0x08000000
TARGET_BASE = 0x3E0000
next_placement = TARGET_BASE

# 1. Place rodata.
data_start, data_size = sections[".rodata"]
rodata = libpick_word[data_start : data_start + data_size]
rom[next_placement : next_placement + len(rodata)] = rodata
placements = {".rodata": next_placement}
next_placement += len(rodata)

# 2. Place functions.
text_start, _ = sections[".text"]
placements[".text"] = next_placement

for name, (text_offset, size, type_) in symbols.items():
    if type_ == "FUNC":
        func_offset = text_start + text_offset
        func_text = libpick_word[func_offset : func_offset + size]
        rom[next_placement : next_placement + size] = func_text
        placements[name] = next_placement
        next_placement += size

# 3. Patch relocations in emplaced function text.
for offset, type_, _, target in relocation_entries:
    reference = placements[".text"] + offset
    match type_:
        case "R_ARM_ABS32":
            rom[reference : reference + 4] = struct.pack(
                "<I", GBA_ROM_DOMAIN + placements[target]
            )
        case "R_ARM_CALL":
            relative_jump = placements[target] - 8 - reference
            assert relative_jump.bit_length() <= 24
            argument = struct.pack("<i", relative_jump // 4)[:-1]
            rom[reference : reference + 4] = argument + b"\xeb"


# Edit original pick_bonus_word function to call our new function.
rom[0x5988:0x5998] = struct.pack(
    "<IIII",
    0xE1A00005,  # mov r5, r0
    0xE1A01004,  # mov r4, r1
    0xE1A00000,  # mov r0, r0 (nop)
    0xEB000000 + (placements["mcmc_word"] - 8 - 0x5994) // 4,  # bl mcmc_word
)

assert len(rom) == 0x400000, hex(len(rom))
open(sys.argv[2], "wb").write(rom)
