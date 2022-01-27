# This file is part of Sympathy for Data.
# Copyright (c) 2016, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import os
import re
import json
import datetime

import numpy as np
import pandas
import six


def base_eval(string, globals_dict=None, mode='eval'):
    """
    Evaluate expression in a standardized environment with a few imports.
    datetime
    numpy as np
    pandas
    re

    globals_dict argument can be used to extend the environment.
    """
    context = {'datetime': datetime,
               'np': np,
               'os': os,
               'json': json,
               'pandas': pandas,
               'six': six,
               're': re}
    if globals_dict:
        context.update(globals_dict)

    compiled = compile(string, "<string>", mode)
    return eval(compiled, context, {})
