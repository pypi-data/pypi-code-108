#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2016-2017, 2019-2020 Chris Lamb <lamby@debian.org>
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

import collections
import functools
import platform
import shutil

try:
    import distro
except ImportError:
    distro = None

from .profiling import profile
from .external_tools import EXTERNAL_TOOLS, REMAPPED_TOOL_NAMES, GNU_TOOL_NAMES

# The output of --help and --list-tools will use the order of this dict.
# Please keep it alphabetized.
OS_NAMES = collections.OrderedDict(
    [
        ("arch", "Arch Linux"),
        ("debian", "Debian"),
        ("FreeBSD", "FreeBSD"),
        ("guix", "GNU Guix"),
    ]
)


@functools.lru_cache()
def find_executable(cmd):
    """
    Given a command name (eg. `dumppdf`), return the absolute path to that
    command. Will also try the command with some common suffixes (eg.
    `dumppdf.py`) to support distributions that strip or retain them.

    Returns `None` if no command is found.
    """

    for suffix in ("", ".py"):
        val = shutil.which(f"{cmd}{suffix}")
        if val:
            return val


def get_tools(only_missing=False):
    """Return the tool configuration in a dict"""

    d = {}

    external_tools = sorted(tool_required.all)
    if only_missing:
        external_tools = [
            tool for tool in external_tools if not tool_check_installed(tool)
        ]
    d["External-Tools-Required"] = tuple(external_tools)

    current_os = get_current_os()
    os_list = [current_os] if (current_os in OS_NAMES) else iter(OS_NAMES)
    for os_ in os_list:
        tools = set()
        for x in external_tools:
            try:
                tools.add(EXTERNAL_TOOLS[x][os_])
            except KeyError:
                pass
        d["Available-in-{}-packages".format(OS_NAMES[os_])] = tuple(
            sorted(tools)
        )

    d["Missing-Python-Modules"] = tuple(sorted(python_module_missing.modules))

    return d


def get_tool_name(tool):
    return REMAPPED_TOOL_NAMES.get(tool, tool)


def tool_prepend_prefix(prefix, *tools):
    if not prefix:
        return
    for tool in tools:
        REMAPPED_TOOL_NAMES[tool] = prefix + tool


def tool_check_installed(command):
    if (
        command == get_tool_name(command)
        and not os_is_gnu()
        and tool_is_gnu(command)
    ):
        # try "g" + command for each tool, if we're on a non-GNU system
        if find_executable("g" + command):
            tool_prepend_prefix("g", command)

    return find_executable(get_tool_name(command))


def tool_required(command):
    """
    Decorator that checks if the specified tool is installed
    """
    from .exc import RequiredToolNotFound

    if not hasattr(tool_required, "all"):
        tool_required.all = set()
    tool_required.all.add(command)

    def wrapper(fn):
        @functools.wraps(fn)
        def tool_check(*args, **kwargs):
            """
            Due to the way decorators are executed at import-time we defer the
            execution of `find_executable` until we actually run the decorated
            function (instead of prematurely returning a different version of
            `tool_check`).

            This ensures that any os.environ['PATH'] modifications are
            performed prior to the `find_executable` tests.
            """
            if not tool_check_installed(command):
                raise RequiredToolNotFound(command)

            with profile("command", command):
                return fn(*args, **kwargs)

        return tool_check

    return wrapper


def tool_is_gnu(command):
    return command in GNU_TOOL_NAMES


def os_is_gnu():
    system = platform.system()
    return system in ("Linux", "GNU") or system.startswith("GNU/")


def get_current_os():
    system = platform.system()
    if system == "Linux":
        if distro:
            return distro.id()
    return system  # noqa


def get_current_distro_like():
    if not distro:
        return []
    return distro.like().split()


def get_package_provider(tool, os=None):
    try:
        providers = EXTERNAL_TOOLS[tool]
    except KeyError:  # noqa
        return None

    try:
        return providers[get_current_os()]
    except KeyError:
        # lookup failed, try to look for a package for a similar distro
        for d in get_current_distro_like():
            try:
                return providers[d]
            except KeyError:
                pass

    return None


def python_module_missing(name):
    python_module_missing.modules.add(name)


python_module_missing.modules = set()
