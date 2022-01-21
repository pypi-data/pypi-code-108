#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2017, 2020-2021 Chris Lamb <lamby@debian.org>
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
import pytest


def test_all_tools_are_listed():
    # Note the ordering of this test (see: f1d744da16)
    from diffoscope.comparators import ComparatorManager
    from diffoscope.external_tools import EXTERNAL_TOOLS
    from diffoscope.tools import tool_required

    ComparatorManager().reload()

    tools = set(tool_required.all)

    for x in tools:
        if x not in EXTERNAL_TOOLS:
            pytest.fail(f"{x} is not present in EXTERNAL_TOOLS")


def test_get_tools():
    # Note the ordering of this test (see: f1d744da16)
    from diffoscope.comparators import ComparatorManager
    from diffoscope.tools import get_tools

    ComparatorManager().reload()

    tools = get_tools()
    missing_tools = get_tools(only_missing=True)
    k = "External-Tools-Required"
    for x in missing_tools[k]:
        if x not in tools[k]:
            pytest.fail(
                f"{x} must be present for {k} in tools and only_missing"
            )


def test_sbin_added_to_path():
    from diffoscope.tools import tool_required

    _, _, filenames = list(os.walk("/sbin"))[0]

    @tool_required(filenames[0])
    def fn():
        pass

    fn()


def test_required_tool_not_found():
    from diffoscope.exc import RequiredToolNotFound
    from diffoscope.tools import tool_required

    @tool_required("does-not-exist")
    def fn():
        pass

    with pytest.raises(RequiredToolNotFound):
        fn()
