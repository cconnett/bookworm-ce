import dataclasses
import string
from typing import List, Tuple

LEX = open("bookworm.gba", "rb").read()
LEX = memoryview(LEX[0xF7C38:])


@dataclasses.dataclass
class Tab:
    is_last: bool
    is_prefix: bool
    is_word: bool
    letter: str

    @classmethod
    def frombyte(cls, b):
        if chr((b & 0x1F) + ord("A")) not in string.ascii_uppercase:
            breakpoint()
        return cls(
            not bool(b & 0x80),
            bool(b & 0x40),
            bool(b & 0x20),
            chr((b & 0x1F) + ord("A")),
        )


def unpack_lexicon(data, prefix):
    if not prefix:
        skip_width = 3
    elif 1 <= len(prefix) < 4:
        skip_width = 2
    else:
        unpack_lexicon_from_list(data, prefix)
        return

    while True:
        tab = Tab.frombyte(data[0])
        bytes_to_skip = unpack_uint(skip_width, data[1:])
        data = data[skip_width + 1 :]
        if tab.is_word:
            print(prefix + tab.letter)
        if tab.is_prefix:
            unpack_lexicon(data[bytes_to_skip:], prefix + tab.letter)
        if tab.is_last:
            break


def unpack_lexicon_from_list(data, prefix):
    data, tabs = read_one_list(data)
    for tab in tabs:
        if tab.is_word:
            print(prefix + tab.letter)
        if tab.is_prefix:
            data = unpack_lexicon_from_list(data, prefix + tab.letter)
    return data


def unpack_uint(length, data):
    ret = 0
    for i in reversed(range(0, length)):
        ret <<= 8
        ret += data[i]
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


if __name__ == "__main__":
    unpack_lexicon(LEX, "")
