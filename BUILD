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

cc_library(
    name = "check_special_words",
    srcs = ["check_special_words.c"],
    hdrs = ["check_special_words.h"],
    copts = [
        "-Wall",
        "-Wextra",
        "-std=c2x",
    ],
    target_compatible_with = [
        "//platforms:armv4t",
    ],
)

genrule(
    name = "new_trie",
    srcs = glob(["word_lists/*.txt"]),
    outs = ["new_dict.bwtrie"],
    cmd = "$(location :word_list_management) $(SRCS) $@",
    tools = [":word_list_management"],
)

genrule(
    name = "bookworm-ce",
    srcs = ["3.gba", ":pick_word", ":check_special_words"],
    outs = ["bookworm-ce.gba"],
    tools = [":linker"],
    cmd = "$(location :linker) $(location :3.gba) $@ $(location :pick_word) $(location :check_special_words)",
)

genrule(
    name = "step_3_minor_patches",
    srcs = [":2.gba"],
    outs = ["3.gba"],
    tools = [":fix_word_validator"],
    cmd = "$(location :fix_word_validator) $(location :2.gba) $@",
)

genrule(
    name = "step_2_audio",
    srcs = [":1.gba", "bone.raw"],
    outs = ["2.gba"],
    tools = [":patch_audio"],
    cmd = "$(location :patch_audio) $(location :1.gba) $@ $(location :bone.raw)",
)

genrule(
    name = "step_1_lexicon",
    srcs = ["bookworm.gba", ":new_dict.bwtrie"],
    outs = ["1.gba"],
    tools = [":replace_lexicon"],
    cmd = "$(location :replace_lexicon) $(location bookworm.gba) $@ $(location :new_dict.bwtrie)",
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
py_binary(
    name = "linker",
    srcs = ["linker.py"],
)
py_binary(
    name = "fix_word_validator",
    srcs = ["fix_word_validator.py"],
)
py_binary(
    name = "replace_lexicon",
    srcs = ["replace_lexicon.py"],
)
py_binary(
    name = "patch_audio",
    srcs = ["patch_audio.py"],
)
