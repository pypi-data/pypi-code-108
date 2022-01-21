# This code is from `click._compat` (Copyright 2014 Pallets, licensed under the BSD license).

import re

_ansi_re = re.compile(r"\033\[[;?0-9]*[a-zA-Z]")


def strip_ansi(value):
    return _ansi_re.sub("", value)
