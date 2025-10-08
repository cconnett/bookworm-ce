cc_library(
    name = "pick_word",
    srcs = ["pick_word.c"],
    hdrs = ["pick_word.h"],
    copts = [
        "-Wall",
        "-Wextra",
        "-std=c2x",
    ],
)

cc_binary(
    name = "test_pick_word",
    srcs = ["test_pick_word.c"],
    copts = [
        "-Wall",
        "-Wextra",
        "-std=c2x",
    ],
    data = [":new_trie"],
    deps = [":pick_word"],
)

genrule(
    name = "new_trie",
    srcs = ["curated_lists/bookworm-ce-1.0.txt"],
    outs = ["new_dict.bwtrie"],
    cmd = "$(location :decode_dict) $(location curated_lists/bookworm-ce-1.0.txt) $@",
    tools = [":decode_dict"],
)

py_binary(
    name = "decode_dict",
    srcs = ["decode_dict.py"],
)

# ARM32 targets
cc_library(
    name = "pick_word_arm",
    srcs = ["pick_word.c"],
    hdrs = ["pick_word.h"],
    copts = [
        "-Wall",
        "-Wextra",
        "-std=c2x",
    ],
    target_compatible_with = [
        "//platforms:armv4t",
    ],
)

cc_binary(
    name = "test_pick_word_arm",
    srcs = ["test_pick_word.c"],
    copts = [
        "-Wall",
        "-Wextra",
        "-std=c2x",
    ],
    data = ["new_dict_final.dat"],
    target_compatible_with = [
        "//platforms:armv4t",
    ],
    deps = [":pick_word_arm"],
)
