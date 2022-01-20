# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2021 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

import io
import json
import sys

import six

if six.PY2:
    from collections import Mapping

    from StringIO import StringIO
else:
    from collections.abc import Mapping  # noqa

    StringIO = io.StringIO

PY_VERSION_MAJOR_MINOR = (sys.version_info.major, sys.version_info.minor)


def json_dump(obj, fp, **kwargs):
    """
    A special version of json.dumps for Python 2.7 and Python 3.5, fp must have been opened in
    binary mode.
    """
    # TODO: Once Python 2.7 and Python 3.5 have been dropped, replace me with json.dump and open fp
    # in text mode instead, it will be faster
    converted_data = json.dumps(obj, **kwargs)

    if isinstance(converted_data, six.text_type):
        converted_data = converted_data.encode("utf-8")

    fp.write(converted_data)
