cc_library(
    name = "pick_word",
    srcs = ["pick_word.c"],
    hdrs = ["pick_word.h"],
    copts = [
        "-Wall",
        "-Wextra",
        "-std=c99",
    ],
)

cc_binary(
    name = "test_pick_word",
    srcs = ["test_pick_word.c"],
    copts = [
        "-Wall",
        "-Wextra",
        "-std=c99",
    ],
    data = ["new_dict_final.dat"],
    deps = [":pick_word"],
)

# ARM32 targets
cc_library(
    name = "pick_word_arm",
    srcs = ["pick_word.c"],
    hdrs = ["pick_word.h"],
    copts = [
        "-Wall",
        "-Wextra",
        "-std=c99",
    ],
    target_compatible_with = [
        "@platforms//cpu:armv7",
    ],
)

cc_binary(
    name = "test_pick_word_arm",
    srcs = ["test_pick_word.c"],
    copts = [
        "-Wall",
        "-Wextra",
        "-std=c99",
    ],
    data = ["new_dict_final.dat"],
    deps = [":pick_word_arm"],
    target_compatible_with = [
        "@platforms//cpu:armv7",
    ],
)

# ARM64 targets
cc_library(
    name = "pick_word_arm64",
    srcs = ["pick_word.c"],
    hdrs = ["pick_word.h"],
    copts = [
        "-Wall",
        "-Wextra",
        "-std=c99",
    ],
    target_compatible_with = [
        "@platforms//cpu:aarch64",
    ],
)

cc_binary(
    name = "test_pick_word_arm64",
    srcs = ["test_pick_word.c"],
    copts = [
        "-Wall",
        "-Wextra",
        "-std=c99",
    ],
    data = ["new_dict_final.dat"],
    deps = [":pick_word_arm64"],
    target_compatible_with = [
        "@platforms//cpu:aarch64",
    ],
)
