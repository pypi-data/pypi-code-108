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
from idict.function.wrapper import call, apply


def df_head(field="df", output="head"):
    """
    >>> from idict import idict
    >>> d = idict.fromtoy(output_format="df")
    >>> d >>= df_head()
    >>> d.head
       attr1  attr2  class
    0    5.1    6.4      0
    1    1.1    2.5      1
    2    6.1    3.6      0
    3    1.1    3.5      1
    4    3.1    2.5      0
    """
    return let(call, field=field, method="head", output=output)


def xywrapper(function, Xin="X", yin="y", Xout="X", yout="y", version=0, **config):
    r"""
    >>> from sklearn.utils import resample
    >>> from idict import idict
    >>> d = idict.fromtoy(output_format="Xy")
    >>> d.y
    array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
    >>> d >>= xywrapper(resample, n_samples=2, random_state=0)
    >>> d.X
        attr1  attr2
    12    2.1    0.1
    15   31.1    4.7
    >>> d.y
    array([0, 1])
    """
    return let(apply, function=function, input=[Xin, yin], output=[Xout, yout], config=config)
