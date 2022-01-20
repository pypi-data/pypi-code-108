# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import pymsalruntime.pymsalruntime as pymsalrt
import atexit

pymsalrt._startup_msalruntime()
atexit.register(pymsalrt._shutdown_msalruntime)

from pymsalruntime.pymsalruntime import *
