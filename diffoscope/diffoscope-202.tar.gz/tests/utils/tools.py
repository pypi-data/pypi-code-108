#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2015      Jérémy Bobbio <lunar@debian.org>
# Copyright © 2016-2017 Mattia Rizzolo <mattia@debian.org>
# Copyright © 2017-2020 Chris Lamb <lamby@debian.org>
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
import functools
import importlib.util
import subprocess

from diffoscope.tools import get_package_provider, find_executable

from ..utils.versions import Version


def file_version():
    return (
        subprocess.check_output(("file", "-v"))
        .decode("utf-8")
        .splitlines()[0]
        .split("-")[-1]
    )


def file_version_is_lt(version):
    return Version(file_version()) < Version(version)


def file_version_is_ge(version):
    return Version(file_version()) >= Version(version)


def tools_missing(*required):
    return not required or any(find_executable(x) is None for x in required)


def skipif(*args, **kwargs):
    """
    Call `pytest.mark.skipif` with the specified arguments.

    If `check_env_for_missing_tools=True` is passed and the
    `DIFFOSCOPE_TESTS_FAIL_ON_MISSING_TOOLS` environment variable is exported,
    this alters the behaviour such that a tool listed within this variable is
    treated as a failed test instead of being skipped.

    For more information on the rationale here, see issue #35.
    """

    if not kwargs.get("check_env_for_missing_tools", False):
        return pytest.mark.skipif(*args, **kwargs)

    key = "DIFFOSCOPE_FAIL_TESTS_ON_MISSING_TOOLS"
    val = os.environ.get(key)

    if val is None:
        return pytest.mark.skipif(*args, **kwargs)

    tools_required = kwargs.get("tools", ())
    missing_tools = val.split() + ["/missing"]  # special value used in tests

    if not tools_required or any(
        x for x in tools_required if x in missing_tools
    ):
        return pytest.mark.skipif(*args, **kwargs)

    msg = "{} ({}={!r})".format(kwargs["reason"], key, val)

    # We cannot simply call pytest.fail here as that would result in a failure
    # during the test collection phase instead when the test is actually
    # executed.
    def outer(*args1, **kwargs1):
        def inner(*args2, **kwargs2):
            if args[0]:  # i.e. the condition of the skipif() is True
                return pytest.fail(msg)
            return None

        return inner

    return outer


def skip_unless_tools_exist(*required):
    return skipif(
        tools_missing(*required),
        reason=reason(*required),
        tools=required,
        check_env_for_missing_tools=True,
    )


def skip_if_tool_version_is(tool, actual_ver, target_ver, vcls=Version):
    if tools_missing(tool):
        return skipif(True, reason=reason(tool), tools=(tool,))
    if callable(actual_ver):
        actual_ver = actual_ver()
    return skipif(
        vcls(str(actual_ver)) == vcls(str(target_ver)),
        reason="requires {} != {} ({} detected)".format(
            tool, target_ver, actual_ver
        ),
        tools=(tool,),
    )


def skip_unless_tool_is_at_least(tool, actual_ver, min_ver, vcls=Version):
    if tools_missing(tool) and module_is_not_importable(tool):
        return skipif(True, reason=reason(tool), tools=(tool,))
    if callable(actual_ver):
        actual_ver = actual_ver()
    return skipif(
        vcls(str(actual_ver)) < vcls(str(min_ver)),
        reason="{} >= {} ({} detected)".format(
            reason(tool), min_ver, actual_ver
        ),
        tools=(tool,),
    )


def skip_unless_tool_is_at_most(tool, actual_ver, max_ver, vcls=Version):
    if tools_missing(tool) and module_is_not_importable(tool):
        return skipif(True, reason=reason(tool), tools=(tool,))
    if callable(actual_ver):
        actual_ver = actual_ver()
    return skipif(
        vcls(str(actual_ver)) > vcls(str(max_ver)),
        reason="{} <= {} ({} detected)".format(
            reason(tool), max_ver, actual_ver
        ),
        tools=(tool,),
    )


def skip_unless_tool_is_between(
    tool, actual_ver, min_ver, max_ver, vcls=Version
):
    if tools_missing(tool):
        return skipif(True, reason=reason(tool), tools=(tool,))
    if callable(actual_ver):
        actual_ver = actual_ver()
    return skipif(
        (vcls(str(actual_ver)) < vcls(str(min_ver)))
        or (vcls(str(actual_ver)) > vcls(str(max_ver))),
        reason="{} min {} >= {} ({} detected)".format(
            reason(tool), min_ver, max_ver, actual_ver
        ),
        tools=(tool,),
    )


def skip_if_binutils_does_not_support_x86():
    if tools_missing("objdump"):
        return skip_unless_tools_exist("objdump")

    return skipif(
        "elf64-x86-64" not in get_supported_elf_formats(),
        reason="requires a binutils capable of reading x86-64 binaries",
        tools=("objdump",),
    )


@functools.lru_cache()
def get_supported_elf_formats():
    try:
        return set(
            subprocess.check_output(("objdump", "--info"))
            .decode("utf-8")
            .splitlines()
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return set()


def module_is_not_importable(x):
    try:
        if importlib.util.find_spec(x) is None:
            return True
        # an existent module is not necessarily importable, e.g. if its child
        # modules are not available, e.g. if we are running diffoscope using a
        # non-default version of python, and the module uses extension modules
        # that haven't been compiled for this version
        importlib.import_module(x)
    except ImportError:
        # Probing for submodules (eg. ``debian.deb822``) will attempt to
        # import ``debian`` so we must handle that failing.
        return True

    return False


def skip_unless_module_exists(name):
    return skipif(
        module_is_not_importable(name),
        reason=f"requires {name} Python module",
        tools=(f"{name}_module",),
    )


def skip_unless_file_version_is_at_least(version):
    return skip_unless_tool_is_at_least("file", file_version, version)


def reason(*tools):
    xs = []

    for x in tools:
        if not tools_missing(x):
            continue
        provider = get_package_provider(x)
        if provider is None:
            xs.append(x)
            continue

        xs.append("{} (try installing {})".format(x, provider))

    return "requires {}".format(" and ".join(xs))
