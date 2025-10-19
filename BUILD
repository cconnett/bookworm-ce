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
    srcs = glob(["word_lists/*.txt"]),
    outs = ["new_dict.bwtrie"],
    cmd = "$(location :word_list_management) $(SRCS) $@",
    tools = [":word_list_management"],
)

py_library(
    name = "decode_dict_lib",
    srcs = ["decode_dict.py"],
)

py_library(
    name = "word_list_management_lib",
    deps = [":decode_dict_lib"],
    srcs = ["word_list_management.py"],
)
py_binary(
    name = "word_list_management",
    deps = [":word_list_management_lib"],
    srcs = ["word_list_management.py"],
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
