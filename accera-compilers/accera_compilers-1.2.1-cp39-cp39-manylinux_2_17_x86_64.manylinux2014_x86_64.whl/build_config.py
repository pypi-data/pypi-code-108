#!/usr/bin/env python3
####################################################################################################
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
# Authors: Mason Remy
# Requires: Python 3.5+
####################################################################################################

import os

__script_path = os.path.dirname(os.path.abspath(__file__))
bin_dir = __script_path # Assume this script is deployed into the install bin dir
root_dir = os.path.abspath(os.path.join(__script_path, os.pardir))

class BuildConfig:
    c_compiler = r""
    cxx_compiler = r"/opt/rh/devtoolset-10/root/usr/bin/c++"
    llvm_symbolizer = r"/opt/vcpkg/installed/x64-linux/tools/llvm/llvm-symbolizer"
    llvm_custom_path = r""
    use_libcxx = r"OFF"
    config_in_build_path = False
    additional_cmake_init_args = r''
    obj_extension = r".o"
    asm_extension = r".s"
    static_library_extension = r".a"
    static_library_prefix = r"lib"
    shared_library_extension = r".so"
    shared_library_prefix = r"lib"
    exe_extension = r""
    vulkan_runtime_wrapper_shared_library = os.path.join(root_dir, r"")
