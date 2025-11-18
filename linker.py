import os.path
import struct
import subprocess
import sys
import tempfile

if len(sys.argv) < 4:
    print(f"Usage: sys.argv[0] infile outfile code.o [...]")
    sys.exit(2)

rom = bytearray(open(sys.argv[1], "rb").read())
GBA_ROM_DOMAIN = 0x08000000
TARGET_BASE = 0x3F0000


def run_readelf(mode, filename):
    proc = subprocess.run(
        ["arm-none-eabi-readelf", f"-{mode}", filename],
        capture_output=True,
        encoding="utf-8",
    )
    proc.check_returncode()
    return proc.stdout.split("\n")


next_placement = TARGET_BASE
placements = {}

# 0. Read from object file.
for obj_filename in sys.argv[3:]:
    match os.path.splitext(obj_filename)[1]:
        case ".a":
            ar_t = subprocess.run(["ar", "t", obj_filename], capture_output=True)
            ar_t.check_returncode()
            o_filename = ar_t.stdout.decode().split("\n")[0]
            ar_p = subprocess.run(
                ["ar", "p", obj_filename, o_filename], capture_output=True
            )
            ar_p.check_returncode()
            libpick_word = ar_p.stdout
        case ".o":
            libpick_word = open(obj_filename, "rb").read()
        case _:
            print("Code must be .a or .o.")
            sys.exit(2)

    with tempfile.NamedTemporaryFile(suffix=".o") as o_file:
        o_file.write(libpick_word)
        o_file.flush()
        section_headers = run_readelf("S", o_file.name)[4:]
        relocation_output = run_readelf("r", o_file.name)[5:]
        symbol_table = run_readelf("s", o_file.name)[5:]

    sections = {
        name: (int(offset, base=16), int(size, base=16))
        for name, type_, addr, offset, size, _ in (
            line[7:].split(maxsplit=5)
            for line in section_headers
            if line.startswith("  [")
        )
    }

    relocation_entries = [
        (int(offset, base=16), type_, int(value, base=16), name)
        for offset, info, type_, value, name in (
            line.split() for line in relocation_output if len(line.split()) == 5
        )
    ]

    symbols = {
        name: (int(value, base=16), int(size), type_)
        for (num, value, size, type_, _, _, _, name) in (
            line.split() for line in symbol_table if len(line.split()) == 8
        )
    }

    # 1. Place rodata.
    for section in sections:
        if section.startswith(".rodata"):
            data_start, data_size = sections[section]
            rodata = libpick_word[data_start : data_start + data_size]
            rom[next_placement : next_placement + len(rodata)] = rodata
            placements[section] = next_placement
            next_placement += len(rodata)

    # 2. Place functions.
    text_start, _ = sections[".text"]
    placements[".text"] = next_placement

    for name, (text_offset, size, type_) in symbols.items():
        if type_ == "FUNC":
            func_offset = text_start + text_offset
            func_text = libpick_word[func_offset : func_offset + size]
            # print(name)
            # print(" ".join(f"{b:02X}" for b in func_text))
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

# Edit original pick_bonus_word function to call our new mcmc_word.
rom[0x5988:0x5998] = struct.pack(
    "<IIII",
    0xE1A00005,  # mov r5, r0
    0xE1A01004,  # mov r4, r1
    0xE1A00000,  # mov r0, r0 (nop)
    0xEB000000 + (placements["mcmc_word"] - 8 - 0x5994) // 4,  # bl mcmc_word
)

# Replace strcmp call in submit_selection with our new checker.
rom[0xB948:0xB94C] = struct.pack(
    "<I", 0xEB000000 + (placements["check_special_words"] - 8 - 0xB948) // 4
)

# Redirect original CalculateScore to new CalculateScore.
print(hex(placements["CalculateScore"]))
rom[0x4C5C:0x4C60] = struct.pack(
    "<I", 0xEA000000 + (placements["CalculateScore"] - 8 - 0x4C5C) // 4
)

assert len(rom) == 0x400000, hex(len(rom))
open(sys.argv[2], "wb").write(rom)
