load("@bazel_tools//tools/build_defs/cc:action_names.bzl", "ACTION_NAMES")
load(
    "@bazel_tools//tools/cpp:cc_toolchain_config_lib.bzl",
    "feature",
    "flag_group",
    "flag_set",
    "tool_path",
)

all_link_actions = [
    ACTION_NAMES.cpp_link_executable,
    ACTION_NAMES.cpp_link_dynamic_library,
    ACTION_NAMES.cpp_link_nodeps_dynamic_library,
]

all_compile_actions = [
    ACTION_NAMES.assemble,
    ACTION_NAMES.c_compile,
    ACTION_NAMES.cpp_compile,
    ACTION_NAMES.cpp_header_parsing,
    ACTION_NAMES.cpp_module_compile,
    ACTION_NAMES.cpp_module_codegen,
    ACTION_NAMES.linkstamp_compile,
    ACTION_NAMES.preprocess_assemble,
]

def _impl(ctx):
    tool_paths = [
        tool_path(
            name = "ar",
            path = "/usr/bin/arm-none-eabi-ar",
        ),
        tool_path(
            name = "cpp",
            path = "/usr/bin/arm-none-eabi-cpp",
        ),
        tool_path(
            name = "gcc",
            path = "/usr/bin/arm-none-eabi-gcc",
        ),
        tool_path(
            name = "gcov",
            path = "/usr/bin/arm-none-eabi-gcov",
        ),
        tool_path(
            name = "ld",
            path = "/usr/bin/arm-none-eabi-ld",
        ),
        tool_path(
            name = "nm",
            path = "/usr/bin/arm-none-eabi-nm",
        ),
        tool_path(
            name = "objcopy",
            path = "/usr/bin/arm-none-eabi-objcopy",
        ),
        tool_path(
            name = "objdump",
            path = "/usr/bin/arm-none-eabi-objdump",
        ),
        tool_path(
            name = "strip",
            path = "/usr/bin/arm-none-eabi-strip",
        ),
    ]

    # ARM4T-specific compiler flags
    arm4t_compile_flags = feature(
        name = "arm4t_flags",
        enabled = True,
        flag_sets = [
            flag_set(
                actions = all_compile_actions,
                flag_groups = [
                    flag_group(
                        flags = [
                            "-mcpu=arm7tdmi",
                            "-march=armv4t",
                            "-mthumb-interwork",
                            "-marm",
                        ],
                    ),
                ],
            ),
        ],
    )

    # ARM4T-specific linker flags
    arm4t_link_flags = feature(
        name = "arm4t_link_flags",
        enabled = True,
        flag_sets = [
            flag_set(
                actions = all_link_actions,
                flag_groups = [
                    flag_group(
                        flags = [
                            "-mcpu=arm7tdmi",
                            "-march=armv4t",
                        ],
                    ),
                ],
            ),
        ],
    )

    cxx_builtin_include_directories = [
        "/usr/lib/gcc/arm-none-eabi/13.2.1/include",
        "/usr/lib/gcc/arm-none-eabi/13.2.1/include-fixed",
        "/usr/include/newlib",
        "/usr/arm-none-eabi/include",
    ]

    return cc_common.create_cc_toolchain_config_info(
        ctx = ctx,
        toolchain_identifier = "arm-none-eabi-toolchain",
        host_system_name = "local",
        target_system_name = "arm-none-eabi",
        target_cpu = "armv4t",
        target_libc = "newlib",
        compiler = "gcc",
        abi_version = "eabi",
        abi_libc_version = "newlib",
        tool_paths = tool_paths,
        features = [arm4t_compile_flags, arm4t_link_flags],
        cxx_builtin_include_directories = cxx_builtin_include_directories,
    )

cc_toolchain_config = rule(
    implementation = _impl,
    attrs = {},
    provides = [CcToolchainConfigInfo],
)
