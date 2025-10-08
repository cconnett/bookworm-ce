package(default_visibility = ["//visibility:public"])

load(":cc_toolchain_config.bzl", "cc_toolchain_config")

# ARM32 (armv4t) toolchain
cc_toolchain_suite(
    name = "arm_toolchain_suite",
    toolchains = {
        "arm": ":arm_toolchain",
    },
)

filegroup(name = "empty")

filegroup(
    name = "all_files",
    srcs = [],
)

cc_toolchain(
    name = "arm_toolchain",
    all_files = ":all_files",
    ar_files = ":all_files",
    compiler_files = ":all_files",
    dwp_files = ":empty",
    linker_files = ":all_files",
    objcopy_files = ":all_files",
    strip_files = ":all_files",
    supports_param_files = 0,
    toolchain_config = ":arm_toolchain_config",
    toolchain_identifier = "arm-none-eabi-toolchain",
)

cc_toolchain_config(
    name = "arm_toolchain_config",
)

toolchain(
    name = "arm_toolchain_registration",
    exec_compatible_with = [
        "@platforms//os:linux",
    ],
    target_compatible_with = [
        "@platforms//cpu:arm",
        "//platforms:armv4t",
    ],
    toolchain = ":arm_toolchain",
    toolchain_type = "@bazel_tools//tools/cpp:toolchain_type",
)
