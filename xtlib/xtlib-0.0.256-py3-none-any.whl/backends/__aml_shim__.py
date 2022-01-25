#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# __aml_shim__.py: AML wants to run a python script, so we use this to launch on shell/batch script
import sys
import os
from xtlib import console

# MAIN code
args = sys.argv[1:]
console.print("__aml_shim__: args=", args)

cmd = args[0]    # all are passed as a logical string (but args[1] is "1", so don't use that)
console.print("__aml_shim__: about to run cmd=", cmd)
os.system(cmd)
