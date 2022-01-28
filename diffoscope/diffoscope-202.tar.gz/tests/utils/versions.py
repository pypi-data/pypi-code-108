#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2021 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl>
#
# diffoscope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# diffoscope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with diffoscope.  If not, see <https://www.gnu.org/licenses/>.

import itertools
import functools
import string


@functools.total_ordering
class Version(str):
    CHARS = string.ascii_letters + string.digits + "~^"
    _ALPHA_ORD = {
        "~": -1,
        "^": +1,
        None: 0,
        **{c: ord(c) for c in string.ascii_letters},
    }

    @staticmethod
    def _len_prefix(s, chars, matching=True):
        for i in range(len(s)):
            if (s[i] in chars) != matching:
                return i
        return len(s)

    @classmethod
    def _cmp_alphabetical(cls, string_a, string_b):
        len_a = cls._len_prefix(string_a, string.ascii_letters + "~^")
        len_b = cls._len_prefix(string_b, string.ascii_letters + "~^")

        for i in range(max(len_a, len_b)):
            a = string_a[i] if i < len_a else None
            b = string_b[i] if i < len_b else None
            c = cls._ALPHA_ORD[a] - cls._ALPHA_ORD[b]
            if c:
                return i, c

        return len_a, 0

    def _cmp(self, other):
        I, J = len(self), len(other)
        i = j = 0

        k = 20

        while i < I or j < J:
            # print(f'{i=} {j=} {self[i:]=!r} {other[j:]=!r}')
            i += self._len_prefix(self[i:], self.CHARS, matching=False)
            j += self._len_prefix(other[j:], self.CHARS, matching=False)

            # print(f'{i=} {j=} {self[i:]=!r} {other[j:]=!r}')

            if (i < I and self[i] in string.digits) or (
                j < J and other[j] in string.digits
            ):
                ii = i + self._len_prefix(self[i:], string.digits)
                jj = j + self._len_prefix(other[j:], string.digits)

                c = (ii == i) - (jj == j)
                # print(f'digits: {c=}')
                if c:
                    return -c

                c = int(self[i:ii]) - int(other[j:jj])
                # print(f'digits: {c=}')

                i, j = ii, jj

            else:
                skip, c = self._cmp_alphabetical(self[i:], other[j:])
                # print(f'alphas: {c=}')

                i += skip
                j += skip

            if c:
                return -1 if c < 0 else +1

            k -= 1
            assert k >= 0

        return 0

    def __eq__(self, other):
        return self._cmp(other) == 0

    def __lt__(self, other):
        return self._cmp(other) < 0
