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
    cxx_compiler = r"C:/Program Files (x86)/Microsoft Visual Studio/2019/Enterprise/VC/Tools/MSVC/14.29.30133/bin/Hostx64/x64/cl.exe"
    llvm_symbolizer = r"C:/Users/VssAdministrator/.conan/data/RoboCodeLLVM/llvmorg-13.0.0/admin/stable/package/0a420ff5c47119e668867cdb51baff0eca1fdb68/bin/llvm-symbolizer.exe"
    llvm_custom_path = r""
    use_libcxx = r"OFF"
    config_in_build_path = True
    additional_cmake_init_args = r'-G "Visual Studio 16 2019" -A x64 -T host=x64'
    obj_extension = r".obj"
    asm_extension = r".s"
    static_library_extension = r".lib"
    static_library_prefix = r""
    shared_library_extension = r".dll"
    shared_library_prefix = r""
    exe_extension = r".exe"
    vulkan_runtime_wrapper_shared_library = os.path.join(root_dir, r"")
