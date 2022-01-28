#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2020 Chris Lamb <lamby@debian.org>
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

import os
import re
import pytest

from diffoscope.main import main


def run(capsys, *args):
    with pytest.raises(SystemExit) as exc:
        main(
            args
            + tuple(
                os.path.join(os.path.dirname(__file__), "data", x)
                for x in ("test1.tar", "test2.tar")
            )
        )

    out, err = capsys.readouterr()

    assert err == ""

    return exc.value.code, out


def test_none(capsys):
    ret, out = run(capsys)
    # Make sure the output doesn't contain any [masked]
    assert re.search(r"\[masked\]", out) is None
    assert ret == 1


def test_all(capsys):
    ret, out = run(capsys, "--diff-mask=.*")

    # Make sure the correct sections were masked
    assert "file list" not in out
    assert "dir/link" not in out

    # Make sure the output contains only [masked]
    # Lines of content start with "│ ", and then either have a +, a - or a space
    # depending on the type of change
    # It should then only contain "[masked]" until the end of the string
    assert re.search(r"│\s[\s\+\-](?!(\[masked\])+)", out) is None
    assert ret == 1


def test_specific(capsys):
    ret, out = run(capsys, "--diff-mask=^Lorem")
    # Make sure only the Lorem ipsum at the start of the line was masked
    assert "[masked] ipsum dolor sit amet" in out
    assert '"Lorem ipsum"' in out
    assert ret == 1
