# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
import shutil
import sys

import pytest

import pybuild
from portmod._cli.pybuild import pybuild_manifest
from portmod.cache import clear_cache_for_path
from portmod.globals import env
from portmod.loader import SandboxedError, _sandbox_execute_pybuild, load_file
from portmod.package import install_pkg, src_prepare, src_unpack
from portmod.perms import Permissions
from portmod.repo import Repo
from portmod.repo.loader import __safe_load_file
from portmod.win32 import get_personal

from .env import TEST_REPO_DIR, rmtree, setup_env, tear_down_env

TMP_REPO = os.path.join(os.path.dirname(env.TMP_DIR), "not-portmod")
TMP_VERSION = 0
TMP_FILE = os.path.join(TMP_REPO, "test", "test", f"test-{TMP_VERSION}.pybuild")

# Windows restricted files are greatly limited due to limitations of Sandboxie,
# but we should test them anyway
if sys.platform == "win32":
    BLOCKED_FILE = os.path.join(get_personal(), "portmod-not-allowed")
else:
    BLOCKED_FILE = os.path.join(os.path.dirname(env.TMP_DIR), "portmod-not-allowed")
env.ALLOW_LOAD_ERROR = False


@pytest.fixture(scope="module", autouse=True)
def setup():
    """
    Sets up and tears down the test environment
    """
    dictionary = setup_env("test")
    env.REPOS.append(Repo("test", TMP_REPO))
    yield dictionary
    tear_down_env()
    rmtree(TMP_REPO)
    rmtree(env.TMP_DIR)


def create_pybuild(filestring, manifest: bool = False):
    global TMP_VERSION, TMP_FILE
    TMP_VERSION += 1
    TMP_FILE = os.path.join(TMP_REPO, "test", "test", f"test-{TMP_VERSION}.pybuild")
    if (
        "{TMP_FILE}" in filestring
        or "{BLOCKED_FILE}" in filestring
        or "{TMP_DIR}" in filestring
    ):
        filestring = filestring.format(
            TMP_FILE=TMP_FILE, BLOCKED_FILE=BLOCKED_FILE, TMP_DIR=env.TMP_DIR
        )
    os.makedirs(env.TMP_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(TMP_FILE), exist_ok=True)
    os.makedirs(os.path.join(TMP_REPO, "profiles"), exist_ok=True)
    clear_cache_for_path(TMP_FILE)

    if sys.platform == "win32":
        filestring = filestring.replace("\\", "\\\\")

    with open(TMP_FILE, "w") as file:
        file.write(filestring)

    with open(BLOCKED_FILE, "w") as file:
        print(file=file)

    with open(os.path.join(TMP_REPO, "profiles", "repo_name"), "w") as file:
        file.write("test")

    with open(os.path.join(TMP_REPO, "profiles", "categories"), "w") as file:
        file.write("test")

    if manifest:
        pybuild_manifest(TMP_FILE)

    return TMP_FILE


def full_load_file(file: str):
    return __safe_load_file(file)


def test_safe():
    """Tests that a simple safe pybuild loads correctly"""
    file = """
from pybuild import Pybuild1

class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"
"""
    create_pybuild(file)
    __safe_load_file(TMP_FILE)


def test_write_globalscope():
    """Tests that writing to files outside TMP_DIR is forbidden in the global scope"""
    file = """
import os
from pybuild import Pybuild1

os.remove("{TMP_FILE}")

class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"
"""
    with pytest.raises(RuntimeError):
        create_pybuild(file)
        full_load_file(TMP_FILE)
    assert os.path.exists(TMP_FILE)


def test_write_globalscope_2():
    """Tests that writing to files within TMP_DIR is forbidden in the global scope"""
    file = """
import os
from pybuild import Pybuild1

os.remove("{TMP_DIR}")

class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"
"""
    with pytest.raises(RuntimeError):
        create_pybuild(file)
        full_load_file(TMP_FILE)
    assert os.path.exists(TMP_FILE)


def test_read_globalscope():
    """Tests that reading from files outside TMP_DIR is forbidden in the global scope"""
    file = """
import os
from pybuild import Pybuild1

assert os.path.exists("{BLOCKED_FILE}")

class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"
"""
    with pytest.raises(RuntimeError):
        create_pybuild(file)
        full_load_file(TMP_FILE)
    assert os.path.exists(TMP_FILE)


def test_read_src_unpack():
    """Tests that reading from files outside TMP_DIR is forbidden within src_unpack"""
    file = """
import os
from pybuild import Pybuild1


class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"

    def src_unpack(self):
        assert os.path.exists("{BLOCKED_FILE}")
"""
    create_pybuild(file)
    mod = load_file(TMP_FILE)
    with pytest.raises(SandboxedError):
        src_unpack(mod, env.TMP_DIR)


@pytest.mark.xfail(
    sys.platform == "win32",
    reason="Sandboxie's permissions don't allow nesting, so we have to use the "
    "default redirected writes, which don't raise exceptions",
)
def test_write_src_unpack():
    """Tests that writing to files outside TMP_DIR is forbidden within src_unpack"""
    file = """
import os
from pybuild import Pybuild1


class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"

    def src_unpack(self):
        os.remove("{TMP_FILE}")
"""
    create_pybuild(file)
    mod = load_file(TMP_FILE)
    with pytest.raises(SandboxedError):
        src_unpack(mod, env.TMP_DIR)
    assert os.path.exists(TMP_FILE)


def test_read_can_update_live():
    """
    Tests that reading from files outside TMP_DIR is forbidden within can_update_live
    """
    file = """
import os
from pybuild import Pybuild1


class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"

    def can_update_live(self):
        assert os.path.exists("{BLOCKED_FILE}")
        return True
"""
    create_pybuild(file)
    mod = load_file(TMP_FILE)
    with pytest.raises(SandboxedError):
        _sandbox_execute_pybuild(mod.FILE, "can-update-live", Permissions(network=True))


@pytest.mark.xfail(
    sys.platform == "win32",
    reason="Sandboxie's permissions don't allow nesting, so we have to use the "
    "default redirected writes, which don't raise exceptions",
)
def test_write_can_update_live():
    """
    Tests that writing to files outside TMP_DIR is forbidden within can_update_live
    """
    file = """
import os
from pybuild import Pybuild1


class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"

    def can_update_live(self):
        os.remove("{TMP_FILE}")
        return True
"""
    create_pybuild(file)
    mod = load_file(TMP_FILE)
    with pytest.raises(SandboxedError):
        _sandbox_execute_pybuild(mod.FILE, "can-update-live", Permissions(network=True))
    assert os.path.exists(TMP_FILE)


def test_read_src_prepare():
    """Tests that reading from files outside TMP_DIR is allowed within src_prepare"""
    file = """
import os
from pybuild import Pybuild1


class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"

    def src_prepare(self):
        assert os.path.exists("{BLOCKED_FILE}")
"""
    create_pybuild(file)
    mod = load_file(TMP_FILE)
    src_prepare(mod, env.TMP_DIR)


@pytest.mark.xfail(
    sys.platform == "win32",
    reason="Sandboxie's permissions don't allow nesting, so we have to use the "
    "default redirected writes, which don't raise exceptions",
)
def test_write_src_prepare():
    """Tests that writing to files outside TMP_DIR is not allowed within src_prepare"""
    file = """
import os
from pybuild import Pybuild1


class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"

    def src_prepare(self):
        os.remove("{TMP_FILE}")
"""
    create_pybuild(file)
    mod = load_file(TMP_FILE)
    with pytest.raises(SandboxedError):
        src_prepare(mod, env.TMP_DIR)
    assert os.path.exists(TMP_FILE)


def test_formatstr():
    """Tests that string.format is banned"""
    file = """
from pybuild import Pybuild1

class Package(Pybuild1):
    NAME="Test"
    DESC="{}".format("Test")
    LICENSE="GPL-3"
"""
    with pytest.raises(NotImplementedError):
        create_pybuild(file)
        __safe_load_file(TMP_FILE)


def test_module_write():
    """Tests that module changes do not propagate from within pybuilds"""
    file = """
import sys
from pybuild import Pybuild1

sys.platform = "foo"

class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"
"""
    old_platform = sys.platform
    create_pybuild(file)
    load_file(TMP_FILE)
    assert sys.platform == old_platform


def test_module_write_2():
    """Tests that module subattribute changes do not propagate from within pybuilds"""
    file = """
import pybuild
from pybuild import Pybuild1

pybuild.Pybuild1.src_install = "foo"

class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"
"""
    create_pybuild(file)
    load_file(TMP_FILE)
    assert pybuild.Pybuild1.src_install != "foo"


def test_module_unsafe_import():
    """Tests that modules cannot be imported indirectly"""
    file = """
from typing import sys
from pybuild import Pybuild1

class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"
"""
    with pytest.raises(SyntaxError):
        create_pybuild(file)
        __safe_load_file(TMP_FILE)


@pytest.mark.xfail(reason="Portability feature not implemented")
def test_module_unsafe_import_2():
    """Tests that modules cannot be accessed indirectly"""
    file = """
import shutil
from pybuild import Pybuild1


class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"
    def src_prepare(self):
        assert shutil.stat is not None
"""
    with pytest.raises(SyntaxError):
        create_pybuild(file)
        pkg = load_file(TMP_FILE)
        src_prepare(pkg, env.TMP_DIR)


def test_underscore():
    """Tests that we can't access names beginning with underscores"""
    file = """
import pybuild
from pybuild import Pybuild1

pybuild.__globals__

class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"
"""
    with pytest.raises(SyntaxError):
        create_pybuild(file)
        __safe_load_file(TMP_FILE)


def test_getattr():
    """Tests that we can't use getattr to access names beginning with underscores"""
    file = """
import os
from pybuild import Pybuild1

class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"

    def src_prepare(self):
        getattr(os.path.join, "__globals__")
"""
    with pytest.raises(SandboxedError):
        create_pybuild(file)
        pkg = load_file(TMP_FILE)
        src_prepare(pkg, env.TMP_DIR)


def test_execute():
    """Tests that we can execute files properly even if we fiddle with platform"""
    file = """
from pybuild import Pybuild1
import sys


class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"

    def src_prepare(self):
        # If this affected the scope of execute, this would
        # raise an unsupported platform exception
        origplatform = sys.platform
        sys.platform = "foo"

        if origplatform == "win32":
            self.execute("dir")
        else:
            self.execute("ls")
"""
    create_pybuild(file)
    mod = load_file(TMP_FILE)
    src_prepare(mod, env.TMP_DIR)


def test_execute_src_prepare_write():
    """Tests that we can't modify files through execute in src_prepare"""
    file = """
from pybuild import Pybuild1
import sys


class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"

    def src_prepare(self):
        # If this affected the scope of execute, this would
        # raise an unsupported platform exception
        origplatform = sys.platform
        sys.platform = "foo"
        if origplatform == "win32":
            self.execute('cmd /c "del {TMP_FILE}"')
        else:
            self.execute("rm {TMP_FILE}")
"""
    create_pybuild(file)
    mod = load_file(TMP_FILE)
    if sys.platform == "win32":
        # Sandboxie won't cause an error when deleting the file fails
        src_prepare(mod, env.TMP_DIR)
    else:
        with pytest.raises(SandboxedError):
            src_prepare(mod, env.TMP_DIR)
    assert os.path.exists(TMP_FILE)


def test_execute_src_prepare_read():
    """Tests that we can read files through execute in src_prepare"""
    file = """
from pybuild import Pybuild1
import sys


class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"

    def src_prepare(self):
        # If this affected the scope of execute, this would
        # raise an unsupported platform exception
        origplatform = sys.platform
        sys.platform = "foo"

        if origplatform == "win32":
            self.execute('dir "{BLOCKED_FILE}"')
        else:
            self.execute("ls {BLOCKED_FILE}")
"""
    create_pybuild(file)
    mod = load_file(TMP_FILE)
    src_prepare(mod, env.TMP_DIR)


def test_execute_src_unpack_read():
    """Tests that we can't read files through execute in src_unpack"""
    file = """
from pybuild import Pybuild1
import sys


class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"

    def src_unpack(self):
        # If this affected the scope of execute, this would
        # raise an unsupported platform exception
        origplatform = sys.platform
        sys.platform = "foo"
        if origplatform == "win32":
            self.execute('dir "{BLOCKED_FILE}"')
        else:
            self.execute("ls {BLOCKED_FILE}")
"""
    create_pybuild(file)
    mod = load_file(TMP_FILE)
    with pytest.raises(SandboxedError):
        src_unpack(mod, env.TMP_DIR)


def test_execute_network_permissions():
    """Tests that network permissions work in src_unpack but not src_prepare"""
    file = """
from pybuild import Pybuild1
import sys

class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"

    def src_unpack(self):
        if sys.platform == "win32":
            self.execute('ping /n 1 1.1.1.1')
        else:
            self.execute('curl 1.1.1.1')

    def src_prepare(self):
        if sys.platform == "win32":
            self.execute('ping /n 1 1.1.1.1')
        else:
            self.execute('curl 1.1.1.1')
"""
    create_pybuild(file)
    mod = load_file(TMP_FILE)
    src_unpack(mod, env.TMP_DIR)
    with pytest.raises(SandboxedError):
        src_prepare(mod, env.TMP_DIR)


def test_execute_permissions_bleed():
    """Tests that network permissions from src_unpack don't bleed into src_prepare"""
    file = """
from pybuild import Pybuild1
import sys

class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"

    def src_unpack(self):
        if sys.platform == "win32":
            self.execute('dir "{TMP_DIR}"')
        else:
            self.execute("ls {TMP_DIR}")

    def src_prepare(self):
        if sys.platform == "win32":
            self.execute('ping /n 1 gitlab.com')
        else:
            self.execute('curl https://gitlab.com')
"""
    create_pybuild(file)
    mod = load_file(TMP_FILE)
    src_unpack(mod, env.TMP_DIR)
    with pytest.raises(SandboxedError):
        src_prepare(mod, env.TMP_DIR)


def test_default():
    """Tests that wrapped functions with default arguments work properly"""
    file = """
from pybuild import Pybuild1
import os


class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"

    def src_prepare(self):
        os.listdir()
"""
    create_pybuild(file)
    mod = load_file(TMP_FILE)
    src_prepare(mod, env.TMP_DIR)


def test_execute_escape():
    """Tests that you can't escape from execute"""
    file = """
from pybuild import Pybuild1
import sys


class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"

    def src_prepare(self):
        if sys.platform == "win32":
            self.execute('& del "{TMP_FILE}"')
        else:
            self.execute("; rm {TMP_FILE}")
"""
    create_pybuild(file)
    mod = load_file(TMP_FILE)
    with pytest.raises(SandboxedError):
        src_prepare(mod, env.TMP_DIR)
    assert os.path.exists(TMP_FILE)


def test_execute_escape_2():
    """Tests that you can't escape from execute"""
    file = """
from pybuild import Pybuild1
import sys


class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"

    def src_prepare(self):
        if sys.platform == "win32":
            self.execute('"& cmd /c "del {TMP_FILE}"')
        else:
            self.execute("; rm {TMP_FILE}")
"""
    create_pybuild(file)
    mod = load_file(TMP_FILE)
    with pytest.raises(SandboxedError):
        src_prepare(mod, env.TMP_DIR)
    assert os.path.exists(TMP_FILE)


def test_safe_open_src_unpack():
    """Tests that you can't use open in src_unpack"""
    file = """
from pybuild import Pybuild1


class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"

    def src_unpack(self):
        with open("{BLOCKED_FILE}", "r") as file:
            file.read()
"""
    create_pybuild(file)
    mod = load_file(TMP_FILE)
    with pytest.raises(SandboxedError):
        src_unpack(mod, env.TMP_DIR)


@pytest.mark.xfail(
    sys.platform == "win32",
    reason="Sandboxie's permissions don't allow nesting, so we have to use the "
    "default redirected writes, which don't raise exceptions",
)
def test_safe_open_src_prepare():
    """Tests that you can't write outside tmpdir with open in src_prepare"""
    file = """
from pybuild import Pybuild1


class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"

    def src_prepare(self):
        with open("{TMP_FILE}", "w") as file:
            print("foo", file=file)
"""
    create_pybuild(file)
    mod = load_file(TMP_FILE)
    with pytest.raises(SandboxedError):
        src_prepare(mod, env.TMP_DIR)


def test_safe_open_allowed():
    """Tests situations where you can use open"""
    file = """
from pybuild import Pybuild1

class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"

    def src_prepare(self):
        with open("{BLOCKED_FILE}", "r") as file:
            file.read()
        with open("{TMP_DIR}/foofile", "w") as file:
            print("foo", file=file)

    def src_unpack(self):
        with open("{TMP_DIR}/foofile", "w") as file:
            print("foo", file=file)
"""
    create_pybuild(file)
    mod = load_file(TMP_FILE)
    src_unpack(mod, env.TMP_DIR)
    src_prepare(mod, env.TMP_DIR)
    os.remove(f"{env.TMP_DIR}/foofile")


def test_stdout():
    """Tests that we can receive stdout from binary executables"""
    file = """
import os
import sys
from pybuild import Pybuild1

class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"

    def src_prepare(self):
        output = self.execute("python --version", pipe_output=True)
        if not output.startswith("Python "):
            raise Exception("Incorrect output " + output)
"""
    create_pybuild(file)
    mod = load_file(TMP_FILE)
    src_prepare(mod, env.TMP_DIR)


def test_git():
    """Tests that we can execute the git executable within the sandbox"""
    file = """
import os
import sys
from pybuild import Pybuild1

class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"

    def src_unpack(self):
        self.execute("git --version")
        self.execute("git clone https://gitlab.com/portmod/blank.git")
        assert os.path.isdir("blank")
        assert os.path.exists(os.path.join("blank", "profiles", "repo_name"))

    def src_prepare(self):
        self.execute("git --version")
"""
    create_pybuild(file)
    mod = load_file(TMP_FILE)
    src_prepare(mod, env.TMP_DIR)
    src_unpack(mod, env.TMP_DIR)


def test_perl():
    """Tests that we can execute the perl executable within the sandbox"""
    if not shutil.which("perl"):
        pytest.skip("Perl not installed")

    file = """
import os
import sys
from pybuild import Pybuild1

class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"

    def src_unpack(self):
        self.execute("perl --version")

    def src_prepare(self):
        self.execute("perl --version")
"""
    create_pybuild(file)
    mod = load_file(TMP_FILE)
    src_prepare(mod, env.TMP_DIR)
    src_unpack(mod, env.TMP_DIR)


def test_loader():
    _sandbox_execute_pybuild(
        os.path.join(TEST_REPO_DIR, "test/test/test-1.0.pybuild"),
        "cache",
        Permissions(),
    )


def test_inplacevar():
    """Tests that inplace modification of variables works"""
    file = """
from pybuild import Pybuild1


class Package(Pybuild1):
    NAME="Test"
    DESC="test"
    LICENSE="GPL-3"

    def __init__(self):
        foo = 0
        foo += 10
        foo -= 1
        foo /= 2
        foo *= 2
        foo //= 2
        foo = 0
        foo |= 2
        foo ^= 2
        foo << 1
        foo >> 1
"""
    create_pybuild(file)
    __safe_load_file(TMP_FILE)


def test_augattribute():
    """Tests that augmented asignment of attributes works"""
    file = """
from pybuild import Pybuild1


class Package(Pybuild1):
    NAME="Test"
    DESC="test"
    LICENSE="GPL-3"

    def __init__(self):
        self.foo = 0
        self.foo += 10
"""
    create_pybuild(file)
    __safe_load_file(TMP_FILE)


def test_path():
    """Tests that path modification from pybuilds with the exec property works"""
    file = """
import os
import stat
from pybuild import Pybuild1


class Package(Pybuild1):
    NAME="Test"
    DESC="test"
    LICENSE="GPL-3"

    def src_install(self):
        os.makedirs(os.path.join(self.D, "bin"))
        path = os.path.join(self.D, "bin", "foo.py")
        with open(path, "w") as file:
            print("#!/usr/bin/env python", file=file)
            print("print(1)", file=file)
        os.chmod(path,
              stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
        )
"""
    create_pybuild(file)

    file2 = """
import shutil
from pybuild import Pybuild1


class Package(Pybuild1):
    NAME="Test"
    DESC="test"
    LICENSE="GPL-3"

    def src_prepare(self):
        # Note: we can't actually execute this as the test data may
        # be installed in a noexec filesystem, as /tmp and /var/tmp
        # sometimes are.
        shutil.which("foo.py")
"""

    pkg = load_file(TMP_FILE)
    install_pkg(pkg, set())

    create_pybuild(file2)
    pkg = load_file(TMP_FILE)
    src_prepare(pkg, env.TMP_DIR)


def test_winreg():
    """
    Tests the registry can be read in windows,
    and that guarded import code doesn't break on other platforms
    """
    file = """
import os
import stat
import sys
from pybuild import Pybuild1

class Package(Pybuild1):
    NAME="Test"
    DESC="test"
    LICENSE="GPL-3"

    def src_prepare(self):
        if sys.platform == "win32":
            from pybuild.winreg import (
                read_reg,
                HKEY_CLASSES_ROOT,
                HKEY_CURRENT_CONFIG,
                HKEY_CURRENT_USER,
                HKEY_LOCAL_MACHINE,
                HKEY_USERS,
            )
            version = read_reg(
                HKEY_LOCAL_MACHINE,
                "SOFTWARE\\Microsoft\\Windows\\CurrentVersion"
            )
            assert version is not None
"""
    create_pybuild(file)

    pkg = load_file(TMP_FILE)
    src_prepare(pkg, env.TMP_DIR)
