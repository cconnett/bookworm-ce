import pprint
import struct
import sys
import wave

if len(sys.argv) < 3:
    print(f"Usage: {sys.argv[0]} infile outfile [extra_samples...]")
    sys.exit(2)

rom = bytearray(open(sys.argv[1], "rb").read())

AUDIO_TABLE_ADDRESS = 0x2A80C
AUDIO_EXPANSION_ADDRESS = 0x3F8000
AUDIO_EXPANSION_BOUNDARY = 0x400000

manifest_length = struct.unpack_from("<iii", rom[AUDIO_TABLE_ADDRESS:])[0]
clip_manifest = list(
    struct.iter_unpack(
        "<iii", rom[AUDIO_TABLE_ADDRESS : AUDIO_TABLE_ADDRESS + manifest_length]
    )
)
clips = [
    (
        rom[AUDIO_TABLE_ADDRESS + offset : AUDIO_TABLE_ADDRESS + offset + length],
        sample_rate,
    )
    for (offset, length, sample_rate) in clip_manifest
]

# Slow Lex's voice.
for index in [15]:
    # "Bonus!" is a little different.
    samples, sample_rate = clips[index]
    clips[index] = (samples, 14000)
for index in range(18, 32):
    samples, sample_rate = clips[index]
    clips[index] = (samples, 12789)

## for i, (samples, sample_rate) in enumerate(clips):
##     with wave.open(f"clips/{i:02d}-{hex(i)}.wav", "wb") as w:
##         w.setnchannels(1)
##         w.setsampwidth(1)
##         w.setframerate(sample_rate)
##         signed_samples = [b for (b,) in struct.iter_unpack("b", samples)]
##         positive_samples = [x + 128 for x in signed_samples]
##         w.writeframesraw(bytes(positive_samples))

for extra in sys.argv[3:]:
    samples = open(extra, "rb").read()
    clips.append((samples, 16000))

new_clip_manifest = []
offset = len(clips) * 3 * 4
clip_address = AUDIO_TABLE_ADDRESS + offset

boundary_address = AUDIO_TABLE_ADDRESS + 459243  # Base audio data segment size
in_expansion = False

for i, (samples, sample_rate) in enumerate(clips):
    if clip_address + len(samples) >= boundary_address:
        print(clip_address + len(samples), boundary_address)
        if in_expansion:
            raise ValueError("Out of space")
        in_expansion = True
        print("--- Jumped to expansion ---")
        clip_address = AUDIO_EXPANSION_ADDRESS
        boundary_address = AUDIO_EXPANSION_BOUNDARY
    rom[clip_address : clip_address + len(samples)] = samples
    new_clip_manifest.append(
        (clip_address - AUDIO_TABLE_ADDRESS, len(samples), sample_rate)
    )
    print(f"Wrote clip {i} to {hex(clip_address)}.")
    clip_address += len(samples)

new_manifest_data = b"".join(
    struct.pack("<iii", offset, length, sample_rate)
    for (offset, length, sample_rate) in new_clip_manifest
)
rom[AUDIO_TABLE_ADDRESS : AUDIO_TABLE_ADDRESS + len(new_manifest_data)] = (
    new_manifest_data
)

print(hex(len(rom)))
open(sys.argv[2], "wb").write(rom)
