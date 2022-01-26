#!/usr/bin/env python3
####################################################################################################
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
# Authors: Mason Remy
# Requires: Python 3.5+
####################################################################################################

import os

__script_path = os.path.dirname(os.path.abspath(__file__))
bin_dir = os.path.join(__script_path, "bin")    # Assume this script is deployed into the install bin dir


class ACCCConfig:
    rc_opt = os.path.join(bin_dir, r"acc-opt")
    argo_translate = os.path.join(bin_dir, r"acc-translate")
    mlir_translate = os.path.join(bin_dir, r"mlir-translate")
    llvm_opt = os.path.join(bin_dir, r"opt")
    llc = os.path.join(bin_dir, r"llc")
    generator_cmakelist = os.path.join(bin_dir, r"accc_templates/CMakeLists.txt.generator.in")
    emitted_lib_cmakelist = os.path.join(bin_dir, r"accc_templates/CMakeLists.txt.emitted_library.in")
    main_cmakelist = os.path.join(bin_dir, r"accc_templates/CMakeLists.txt.main.in")
    main_deploy_dir_name = r"deploy"
    main_deploy_target_type_tag = r"$MAIN_DEPLOY_TARGET_TYPE$"
    library_name_tag = r"$LIBRARY_NAME$"
    main_basename_tag = r"$MAIN_BASENAME$"
    program_name_tag = r"$PROGRAM_NAME$"
    dsl_file_basename_tag = r"$DSL_FILE_BASENAME$"
    dllmain_cc_contents = """#include <windows.h>
BOOL APIENTRY DllMain(HMODULE, DWORD, LPVOID) { return TRUE; }
"""
