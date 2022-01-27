#  Copyright (c) 2021. Davi Pereira dos Santos
#  This file is part of the i-dict project.
#  Please respect the license - more about this in the section (*) below.
#
#  i-dict is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  i-dict is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with i-dict.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and it is unethical regarding the effort and
#  time spent here.
#
from idict import let


def copy(source=None, target=None, **kwargs):
    """
    >>> from idict import idict
    >>> d = idict(x=1) >> let(copy, source="x", target="y")
    >>> d.evaluate()
    >>> d.show(colored=False)
    {
        "y": 1,
        "x": 1,
        "_id": "oRMtnOOH9BxWdFsehRX6pghgYjrwDfaOqWWvzOrq",
        "_ids": {
            "y": "-LB1NvNGUQykT.y2QQGy1E4GbwgwDfaOqWWvzOrq",
            "x": "fH_5142f0a4338a1da2ca3159e2d1011981ac890 (content: l8_09c7059156c4ed2aea46243e9d4b36c01f272)"
        }
    }
    """
    return {target: kwargs[source]}


trcopy = let(copy, source="Xtr", target="X") >> let(copy, source="ytr", target="y")
tscopy = let(copy, source="Xts", target="X") >> let(copy, source="yts", target="y")
# TODO (minor):  finish copy
