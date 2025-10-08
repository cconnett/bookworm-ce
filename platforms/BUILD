package(default_visibility = ["//visibility:public"])

# Define armv4t CPU constraint
constraint_setting(
    name = "cpu_variant",
)

constraint_value(
    name = "armv4t",
    constraint_setting = ":cpu_variant",
)

# ARM32 platform (armv4t)
platform(
    name = "arm",
    constraint_values = [
        "@platforms//cpu:arm",
        ":armv4t",
        # "@platforms//os:none",
    ],
)
