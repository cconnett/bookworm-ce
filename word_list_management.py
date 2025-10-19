import glob
import os.path
import re
import string
import sys
import warnings

import decode_dict

naked_q = re.compile(r"Q([^U]|$)")


def read_word_list(filename, *, verbose=False):
    """Reads a file of words and returns those playable in Bookworm.

    Criteria:
     - Three letters or more
     - Twelve tiles or less (QU is one tile)
     - Q must be followed by U

    All words become uppercased.
    """
    with open(filename) as file:
        words = set()

        bad_chars = 0
        short_count = 0
        long_count = 0
        naked_qs = 0

        def vprint(*args):
            if verbose:
                print(*args)

        for line in file:
            word = line.split("#")[0]
            word = word.strip().casefold().upper()
            if not word:
                continue
            if not word.isalpha():
                warnings.warn(
                    f"{os.path.basename(filename)}: {word!r} "
                    "cannot be encoded (invalid characters)."
                )
                bad_chars += 1
                continue
            tiles = len(word) - word.count("QU")
            if len(word) < 3:
                vprint(f"{os.path.basename(filename)}: {word!r} is too short.")
                short_count += 1
                continue
            if tiles > 12:
                vprint(f"{os.path.basename(filename)}: {word!r} is too long.")
                long_count += 1
                continue
            if naked_q.search(word):
                vprint(f"{os.path.basename(filename)}: {word!r} contains a naked Q.")
                naked_qs += 1
                continue
            if word in words:
                warnings.warn(f"{os.path.basename(filename)}: {word!r} is duplicated.")
                continue
            words.add(word)
        print(
            f"{os.path.basename(filename)}: {len(words)} words; excluded\n"
            f"\t{short_count} too short words and\n"
            f"\t{long_count} too long words and\n"
            f"\t{naked_qs} naked Q words."
        )
        return words


def read_word_dir(path, *, verbose=False):
    words = set()
    for filename in glob.glob(path, recursive=True):
        words.update(read_word_list(filename, verbose=verbose))
    return words


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} input1 [input2...] output.bwtrie")
        sys.exit(1)
    words = set()
    for filename in sys.argv[1:-1]:
        words.update(read_word_dir(filename))
    data = decode_dict.encode_tree(decode_dict.make_tree(words))
    open(sys.argv[-1], "wb").write(data)
