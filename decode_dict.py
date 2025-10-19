import collections
import dataclasses
import logging
import pprint
import random
import string
import struct
import sys
from typing import List, Tuple

import numpy as np
import tqdm
from scipy.stats import chisquare

letter_values = dict(
    zip(
        string.ascii_uppercase,
        [1, 4, 4, 3, 1, 5, 3, 5, 1, 8, 7, 2, 4, 2, 1, 4, 7, 2, 1, 2, 2, 5, 6, 8, 6, 10],
    )
)


def get_lex():
    LEX = open("bookworm.gba", "rb").read()
    LEX = memoryview(LEX[0xF7C38:])
    return LEX


def letter_score(word):
    return sum(letter_values[letter] for letter in word)


@dataclasses.dataclass
class Tab:
    is_last: bool
    is_prefix: bool
    is_word: bool
    letter: str

    @classmethod
    def frombyte(cls, b):
        if (c := chr((b & 0x1F) + ord("A"))) not in string.ascii_uppercase:
            # print(f"Warning: byte {b:02X} decodes to {c}")
            # breakpoint()
            pass
        return cls(
            not bool(b & 0x80),
            bool(b & 0x40),
            bool(b & 0x20),
            chr((b & 0x1F) + ord("A")),
        )


def check_word(data, word):
    i = 0
    head = word[0]
    lex_ref_2 = data
    bit6_count = 0
    rest = word[1:]
    while True:  # do
        while True:  # while (true)
            lex_ref = lex_ref_2
            tab = Tab.frombyte(lex_ref[0])
            logging.debug(f"Searching for {head}: {fmtvec(lex_ref_2)}")
            lex_ref = lex_ref[1:]
            if tab.letter == head:
                break
            if tab.is_last:
                return False
            if tab.is_prefix:
                bit6_count += 1
                logging.debug(f"up1: {bit6_count}")
            lex_ref_2 = lex_ref
            if i < 4:
                if i == 0:
                    lex_ref_2 = lex_ref[3:]
                else:
                    lex_ref_2 = lex_ref[2:]
        if not rest:
            return tab.is_word
        if not tab.is_prefix:
            # This check is not in the original algorithm. Removing this check
            # results in accepting "HOOVEDE" among others.
            return False
        head = rest[0]
        if i < 4:
            if i == 0:
                next_datum = lex_ref[3:]
                jump_size_addend = unpack_uint(3, lex_ref)
            else:
                next_datum = lex_ref[2:]
                jump_size_addend = unpack_uint(2, lex_ref)
            bit6_count = 0
            logging.debug(f"jumped {jump_size_addend} (0x{jump_size_addend:04X}) bytes")
            lex_ref_2 = next_datum[jump_size_addend:]
            logging.debug(f"After jump: {fmtvec(lex_ref_2)}")
        else:
            while True:
                lex_ref_2 = lex_ref
                if tab.is_last:
                    break
                tab = Tab.frombyte(lex_ref[0])
                lex_ref = lex_ref[1:]
            logging.debug(f"Discarded remainder. {fmtvec(lex_ref_2)}")
            while True:  # for (; lex_ref_2 = lex_ref_2, 0 < count_of_bits_6_r5;
                if bit6_count <= 0:
                    break
                bit6_count -= 1
                logging.debug(f"down: {bit6_count}")
                while True:  # do
                    tab3 = Tab.frombyte(lex_ref_2[0])
                    lex_ref_2 = lex_ref_2[1:]
                    if tab3.is_prefix:
                        bit6_count += 1
                        logging.debug(f"up2: {bit6_count}")
                    if tab3.is_last:
                        break
            logging.debug(f"Discarded nested lists. {fmtvec(lex_ref_2)}")
        i += 1
        rest = rest[1:]


def fmtvec(d, length=8):
    return " ".join(f"{b:02X}" for b in d[:length])


def unpack_lexicon(data, prefix=""):
    if not prefix:
        skip_width = 3
    elif 1 <= len(prefix) < 4:
        skip_width = 2
    else:
        yield from unpack_lexicon_from_list(data, prefix)
        return

    while True:
        tab = Tab.frombyte(data[0])
        bytes_to_skip = unpack_uint(skip_width, data[1:])
        if bytes_to_skip >= len(data):
            breakpoint()
        data = data[skip_width + 1 :]
        if tab.is_word:
            yield prefix + tab.letter
        if tab.is_prefix:
            yield from unpack_lexicon(data[bytes_to_skip:], prefix + tab.letter)
        if tab.is_last:
            break


def unpack_lexicon_from_list(data, prefix):
    data, tabs = read_one_list(data)
    for tab in tabs:
        if tab.is_word:
            yield prefix + tab.letter
        if tab.is_prefix:
            data = yield from unpack_lexicon_from_list(data, prefix + tab.letter)
    return data


def unpack_uint(length, data):
    ret = 0
    for i in reversed(range(0, length)):
        ret <<= 8
        ret += data[i]
    return ret


def pack_uint(length, value):
    ret = []
    while value or len(ret) < length:
        value, byte = divmod(value, 256)
        ret.append(byte)
    if len(ret) > length:
        raise OverflowError(f"{ret} does not fit in {length} bytes.")
    return ret


def read_one_list(data: memoryview) -> Tuple[int, List[Tab]]:
    index = 0
    tabs = []
    while True:
        tab = Tab.frombyte(data[index])
        tabs.append(tab)
        index += 1
        if tab.is_last:
            break
    return data[index:], tabs


def complete_list_length(data) -> int:
    depth = 1
    index = 0
    while depth:
        index, tabs = read_one_list(data[index:])
        depth += sum(tab.is_prefix for tab in tabs)
        depth -= 1
    return index


def find_bugged_words():
    full = set(line.strip() for line in open("bookworm_dict.txt").readlines())
    open_set = set(full)
    while open_set:
        new = set()
        for word in tqdm.tqdm(open_set):
            for ext in string.ascii_uppercase:
                probe_word = word + ext
                if probe_word not in full and check_word(get_lex(), probe_word):
                    new.add(probe_word)
        full |= open_set
        full |= new
        open_set = new
    open("new_bugged.txt", "w").write("\n".join(sorted(full)) + "\n")


class Tree(dict):
    def __init__(self):
        super().__init__(self)
        self.is_word = False


def make_tree(words):
    tree = Tree()
    for word in words:
        if word:
            tree.setdefault(word[0], []).append(word[1:])
        else:
            tree.is_word = True
    for letter, extensions in tree.items():
        tree[letter] = make_tree(extensions)
    return tree


def encode_tree(tree, prefix=""):
    level = len(prefix)
    jump_width = 0
    if level == 0:
        jump_width += 1
    if level < 4:
        jump_width += 2
    open_letters = [letter for letter, subtree in tree.items() if subtree]
    # track subencoding for each open letter relative to the end of the current list
    subencoding_start_positions = {}
    rest = b""
    for letter in open_letters:
        subencoding_start_positions[letter] = len(rest)
        rest += encode_tree(tree[letter], prefix=prefix + letter)
    segment = []
    for i, (letter, subtree) in enumerate(tree.items()):
        byte = 0b1000_0000
        byte |= (ord(letter) - 1) & 0x1F
        if subtree.is_word:
            byte |= 0b0010_0000
        if subtree:
            byte |= 0b0100_0000
        segment.append(byte)

        if jump_width:
            jump_value = 0
            if subtree:
                jump_value = subencoding_start_positions[letter] + (1 + jump_width) * (
                    len(tree) - 1 - i
                )
            segment.extend(pack_uint(jump_width, jump_value))
    segment[-1 - jump_width] &= 0b0111_1111
    this_section = bytes(segment)
    if level < 0:
        print(prefix)
        print(open_letters)
        print(" " * level, ":", " ".join(f"{b:02X}" for b in this_section))
    return this_section + rest


def random_word(tree, length=5) -> Tuple[str, int]:
    while True:
        try:
            current = tree
            choice_factor = 1
            word = []
            for _ in range(length - 1):
                branches = [
                    (letter, subtree) for letter, subtree in current.items() if subtree
                ]
                letter, current = random.choice(branches)
                choice_factor *= len(branches)
                word.append(letter)
            leaves = [
                (letter, leaf) for letter, leaf in current.items() if leaf.is_word
            ]
            letter, leaf = random.choice(leaves)
            word.append(letter)
            return ("".join(word), choice_factor)
        except IndexError:
            continue


def mcmc_word(tree, length=5):
    champion, champ_factor = random_word(tree, length)
    for i in range(2, 12):
        challenger, challenger_factor = random_word(tree, length)
        target = challenger_factor / (challenger_factor + champ_factor * i)
        if random.random() < target:
            champion = challenger
            champ_factor = challenger_factor
    return champion


def do_chisquare_test():
    words = list(unpack_lexicon(get_lex()))
    tree = make_tree(words)
    print("Go")
    dist = collections.Counter(word[0] for word in words if len(word) == 5)
    obs = collections.Counter()
    for seed in range(10000):
        obs.update(mcmc_word(tree, 5)[0])

    f_obs = np.array([obs[letter] for letter in string.ascii_uppercase])
    f_exp = np.array([dist[letter] for letter in string.ascii_uppercase])
    pprint.pprint(
        list(zip(string.ascii_uppercase, f_obs / sum(f_obs), f_exp / sum(f_exp)))
    )
    print(
        chisquare(
            f_obs=f_obs / sum(f_obs),
            f_exp=f_exp / sum(f_exp),
        )
    )


if __name__ == "__main__":
    # print(len(words))
    # find_bugged_words()
    # random.seed(50)
    words = [w.strip() for w in open(sys.argv[1]).readlines()]
    # words = sorted(random.sample(words, 5000))
    words = sorted(words)
    data = encode_tree(make_tree(words))
    # logging.getLogger().setLevel(logging.DEBUG)
    # print(check_word(data, "QUALMH"))
    # words2 = list(unpack_lexicon(data, ""))

    # if set(words) != set(words2):
    #    pprint.pprint(set(words) - set(words2))
    #    pprint.pprint(set(words2) - set(words))
    open(sys.argv[2], "wb").write(data)
    # do_chisquare_test()
