# Copyright CNRS/Inria/UCA
# Contributor(s): Eric Debreuve (since 2021)
#
# eric.debreuve@cnrs.fr
#
# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

from string import ascii_uppercase as ASCII_UPPERCASE
from typing import Tuple


MIN_ASCII = 33
MAX_ASCII = 126


def ShortID(python_id: int, /) -> str:
    """"""
    output = []

    digits = tuple(int(_dgt) for _dgt in tuple(str(python_id)))
    n_digits = digits.__len__()

    d_idx = 0
    ascii_value = 0
    while d_idx < n_digits:
        new_ascii = 10 * ascii_value + digits[d_idx]
        if new_ascii > MAX_ASCII:
            if ascii_value >= MIN_ASCII:
                output.append(chr(ascii_value))
            else:
                output.append(str(ascii_value))
            while (d_idx < n_digits) and (digits[d_idx] == 0):
                output.append("0")
                d_idx += 1
            if d_idx < n_digits:
                ascii_value = digits[d_idx]
            else:
                ascii_value = None
        else:
            ascii_value = new_ascii
        d_idx += 1

    if ascii_value is not None:
        if ascii_value >= MIN_ASCII:
            output.append(chr(ascii_value))
        else:
            output.append(str(ascii_value))

    return "".join(output)


def AlphaColumnFromIndex(index: int) -> str:
    """
    index: 0-based
    """
    return AlphaColumnFromLabel(index + 1)


def AlphaColumnFromLabel(label: int) -> str:
    """
    label: 1-based

    Adapted from: https://stackoverflow.com/questions/48983939/convert-a-number-to-excel-s-base-26
    Answer: poke, Feb 26 '18 at 9:00 (https://stackoverflow.com/a/48984697)
    """

    def _DivmodExcel(number: int) -> Tuple[int, int]:
        quotient, remainder = divmod(number, 26)
        if remainder > 0:
            return quotient, remainder
        else:
            return quotient - 1, remainder + 26

    output = []

    while label > 0:
        label, digit = _DivmodExcel(label)
        output.append(ASCII_UPPERCASE[digit - 1])

    return "".join(reversed(output))
