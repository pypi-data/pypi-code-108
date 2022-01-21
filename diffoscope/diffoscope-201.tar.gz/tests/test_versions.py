#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2021      Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl>
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

from .utils.versions import Version

import pytest

cases = [
    ("1.0", "1.0", 0),
    ("1.0", "2.0", -1),
    ("2.0", "1.0", 1),
    ("2.0.1", "2.0.1", 0),
    ("2.0", "2.0.1", -1),
    ("2.0.1", "2.0", 1),
    ("2.0.1a", "2.0.1a", 0),
    ("2.0.1a", "2.0.1", 1),
    ("2.0.1", "2.0.1a", -1),
    ("5.5p1", "5.5p1", 0),
    ("5.5p1", "5.5p2", -1),
    ("5.5p2", "5.5p1", 1),
    ("5.5p10", "5.5p10", 0),
    ("5.5p1", "5.5p10", -1),
    ("5.5p10", "5.5p1", 1),
    ("10xyz", "10.1xyz", -1),
    ("10.1xyz", "10xyz", 1),
    ("xyz10", "xyz10", 0),
    ("xyz10", "xyz10.1", -1),
    ("xyz10.1", "xyz10", 1),
    ("xyz.4", "xyz.4", 0),
    ("xyz.4", "8", -1),
    ("8", "xyz.4", 1),
    ("xyz.4", "2", -1),
    ("2", "xyz.4", 1),
    ("5.5p2", "5.6p1", -1),
    ("5.6p1", "5.5p2", 1),
    ("5.6p1", "6.5p1", -1),
    ("6.5p1", "5.6p1", 1),
    ("6.0.rc1", "6.0", 1),
    ("6.0", "6.0.rc1", -1),
    ("10b2", "10a1", 1),
    ("10a2", "10b2", -1),
    ("1.0aa", "1.0aa", 0),
    ("1.0a", "1.0aa", -1),
    ("1.0aa", "1.0a", 1),
    ("10.0001", "10.0001", 0),
    ("10.0001", "10.1", 0),
    ("10.1", "10.0001", 0),
    ("10.0001", "10.0039", -1),
    ("10.0039", "10.0001", 1),
    ("4.999.9", "5.0", -1),
    ("5.0", "4.999.9", 1),
    ("20101121", "20101121", 0),
    ("20101121", "20101122", -1),
    ("20101122", "20101121", 1),
    ("2_0", "2_0", 0),
    ("2.0", "2_0", 0),
    ("2_0", "2.0", 0),
    # Additional nastiness
    ("2_0.", "2_0", 0),
    ("2..0", "2_0__", 0),
    ("2_0", "__2.0", 0),
    ("2_1.", "2_0", +1),
    ("2..1", "2_0__", +1),
    ("2_1", "__2.0", +1),
    ("2_1.", "2_2", -1),
    ("2..1", "2_2__", -1),
    ("2_1", "__2.2", -1),
    # https://bugzilla.redhat.com/178798
    ("a", "a", 0),
    ("a+", "a+", 0),
    ("a+", "a_", 0),
    ("a_", "a+", 0),
    ("+a", "+a", 0),
    ("+a", "_a", 0),
    ("_a", "+a", 0),
    ("+_", "+_", 0),
    ("_+", "+_", 0),
    ("_+", "_+", 0),
    ("+", "_", 0),
    ("_", "+", 0),
    # Basic testcases for tilde sorting
    ("1.0~rc1", "1.0~rc1", 0),
    ("1.0~rc1", "1.0", -1),
    ("1.0", "1.0~rc1", 1),
    ("1.0~rc1", "1.0~rc2", -1),
    ("1.0~rc2", "1.0~rc1", 1),
    ("1.0~rc1~git123", "1.0~rc1~git123", 0),
    ("1.0~rc1~git123", "1.0~rc1", -1),
    ("1.0~rc1", "1.0~rc1~git123", 1),
    ("a", "a", 0),
    ("a~", "a", -1),
    ("a~~", "a", -1),
    ("a~~~", "a", -1),
    ("a~~~^", "a", -1),
    ("a^", "a", +1),
    ("a^", "a", +1),
    ("a^", "a^", 0),
    ("a^", "a^^", -1),
    ("a^b", "a^^", +1),
    # Basic testcases for caret sorting
    ("1.0^", "1.0^", 0),
    ("1.0^", "1.0", 1),
    ("1.0", "1.0^", -1),
    ("1.0^git1", "1.0^git1", 0),
    ("1.0^git1", "1.0", 1),
    ("1.0", "1.0^git1", -1),
    ("1.0^git1", "1.0^git2", -1),
    ("1.0^git2", "1.0^git1", 1),
    ("1.0^git1", "1.01", -1),
    ("1.01", "1.0^git1", 1),
    ("1.0^20160101", "1.0^20160101", 0),
    ("1.0^20160101", "1.0.1", -1),
    ("1.0.1", "1.0^20160101", 1),
    ("1.0^20160101^git1", "1.0^20160101^git1", 0),
    ("1.0^20160102", "1.0^20160101^git1", 1),
    ("1.0^20160101^git1", "1.0^20160102", -1),
    # Basic testcases for tilde and caret sorting
    ("1.0~rc1^git1", "1.0~rc1^git1", 0),
    ("1.0~rc1^git1", "1.0~rc1", 1),
    ("1.0~rc1", "1.0~rc1^git1", -1),
    ("1.0^git1~pre", "1.0^git1~pre", 0),
    ("1.0^git1", "1.0^git1~pre", 1),
    ("1.0^git1~pre", "1.0^git1", -1),
    # Additional testing for zeroes
    ("0", "0", 0),
    ("0", "00", 0),
    ("0", "000", 0),
    ("00", "000", 0),
    ("000", "000", 0),
    ("00", "0", 0),
    ("000", "0", 0),
    ("0", "0.0", -1),
    ("0.0", "0", +1),
    ("0~", "0", -1),
    ("0^", "0", +1),
    ("0^", "0^", 0),
    ("0^", "0^~", 1),
]


@pytest.mark.parametrize("a,b,expected", cases)
def test_version_comparisons(a, b, expected):
    assert Version(a)._cmp(b) == expected


@pytest.mark.parametrize("a,b", [c[:2] for c in cases if c[2] < 0])
def test_version_lt(a, b):
    assert Version(a) < b
    assert Version(a) < Version(b)


@pytest.mark.parametrize("a,b", [c[:2] for c in cases if c[2] > 0])
def test_version_gt(a, b):
    assert Version(a) > b
    assert Version(a) > Version(b)


@pytest.mark.parametrize("a,b", [c[:2] for c in cases if c[2] == 0])
def test_version_gt(a, b):
    assert Version(a) == b
    assert Version(a) == Version(b)
