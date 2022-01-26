# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Config sorting tests

Note that for the purposes of speed, mods are not removed between tests, and the
removal test occurs at the end. This means that the order of tests may matter,
and you should, when writing tests, assume an arbitrary configuration at the
beginning of the test, and attempt to place the test in such an order as to minimize
the number of changes required to get the desired configuration
"""

import filecmp
import os
import sys
from zipfile import ZipFile

import pytest

from portmod.config.use import add_use, remove_use
from portmod.globals import env
from portmod.loader import load_installed_pkg
from portmod.merge import configure
from portmod.tsort import CycleException
from portmod.vfs import _cleanup_tmp_archive_dir, extract_archive_file_to_tmp, sort_vfs
from portmodlib.archives import list_archive
from portmodlib.atom import Atom
from portmodlib.vfs import find_file, get_vfs_dirs, list_dir

from .env import setup_env, tear_down_env


@pytest.fixture(scope="module", autouse=True)
def setup():
    """
    Sets up and tears down the test environment
    """
    dictionary = setup_env("test-config")
    config = dictionary["config"]
    config_ini = dictionary["config_ini"]
    with open(env.prefix().CONFIG, "w") as configfile:
        print(
            f"""
TEST_CONFIG = "{config}"
TEST_CONFIG_INI = "{config_ini}"
""",
            file=configfile,
        )
    yield dictionary
    tear_down_env()


def test_sort_vfs(setup):
    """
    Tests that sorting the config files works properly
    """
    # Install mods
    configure(
        ["test/test-1.0", "test/test2-1.0"],
        no_confirm=True,
        update=True,
    )
    pkg1 = load_installed_pkg(Atom("test/test-1.0"))
    pkg2 = load_installed_pkg(Atom("test/test2"))
    assert pkg1 and pkg2
    path1 = os.path.normpath(
        os.path.join(env.prefix().ROOT, pkg1._get_install_dir_dest())
    )
    path2 = os.path.normpath(
        os.path.join(env.prefix().ROOT, pkg2._get_install_dir_dest())
    )

    # Check that config is correct
    lines = get_vfs_dirs()
    assert path1 in lines
    assert path2 in lines
    assert lines.index(path1) < lines.index(path2)


def test_user_override(setup):
    """
    Tests that user overrides for vfs sorting work properly
    """
    installpath = os.path.join(env.prefix().CONFIG_DIR, "config", "install.csv")
    os.makedirs(os.path.dirname(installpath), exist_ok=True)

    pkg1 = load_installed_pkg(Atom("test/test"))
    pkg2 = load_installed_pkg(Atom("test/test2"))
    assert pkg1 and pkg2
    path1 = os.path.normpath(
        os.path.join(env.prefix().ROOT, pkg1._get_install_dir_dest())
    )
    path2 = os.path.normpath(
        os.path.join(env.prefix().ROOT, pkg2._get_install_dir_dest())
    )

    # Enforce that test overrides test2
    with open(installpath, "w") as file:
        print("test/test, test/test2", file=file)

    configure(
        ["test/test-1.0", "test/test2-1.0"],
        no_confirm=True,
        update=True,
    )
    sort_vfs()

    # Check that config is correct
    lines = get_vfs_dirs()
    assert path1 in lines
    assert path2 in lines
    assert lines.index(path1) > lines.index(path2)

    # Enforce that test2 overrides test
    with open(installpath, "w") as file:
        print("test/test2, test/test", file=file)

    sort_vfs()

    # Check that config is correct
    lines = get_vfs_dirs()
    assert path1 in lines
    assert path2 in lines
    assert lines.index(path1) < lines.index(path2)

    os.remove(installpath)


def test_user_cycle(setup):
    """
    Tests that cycles introduced by the user are reported correctly
    """
    installpath = os.path.join(env.prefix().CONFIG_DIR, "config", "install.csv")
    os.makedirs(os.path.dirname(installpath), exist_ok=True)

    # Enforce that test overrides test2
    with open(installpath, "w") as file:
        print("test/test, test/test2", file=file)
        print("test/test2, test/test", file=file)

    try:
        with pytest.raises(CycleException):
            configure(
                ["test/test-1.0", "test/test2-1.0"],
                no_confirm=True,
                update=True,
            )
            sort_vfs()
    finally:
        os.remove(installpath)


def test_data_override_flag(setup):
    """
    Tests that mods can conditionally override other mods using DATA_OVERRIDES
    depending on the value of a use flag on the target mod
    """
    # Install mods
    remove_use("foo")
    configure(
        ["test/test6-1.0", "test/test7-1.0"],
        no_confirm=True,
        update=True,
    )
    sort_vfs()

    pkg1 = load_installed_pkg(Atom("test/test6"))
    pkg2 = load_installed_pkg(Atom("test/test7"))
    assert pkg1 and pkg2
    path1 = os.path.normpath(
        os.path.join(env.prefix().ROOT, pkg1._get_install_dir_dest())
    )
    path2 = os.path.normpath(
        os.path.join(env.prefix().ROOT, pkg2._get_install_dir_dest())
    )

    # Check that config is correct
    lines = get_vfs_dirs()
    assert path1 in lines
    assert path2 in lines
    assert lines.index(path1) < lines.index(path2)

    add_use("foo")
    configure(["test/test7-1.0"], no_confirm=True, update=True)
    sort_vfs()

    lines = get_vfs_dirs()
    assert path1 in lines
    assert path2 in lines
    assert lines.index(path1) > lines.index(path2)


def test_find_file(setup):
    """
    Tests that find_file returns the correct file (last in the vfs order)
    """
    configure(
        ["test/test6-1.0", "test/test7-1.0[foo]"],
        no_confirm=True,
        update=True,
    )
    pkg1 = load_installed_pkg(Atom("test/test6"))
    assert pkg1
    assert os.path.abspath(os.path.normpath(find_file("foo.txt"))).startswith(
        os.path.normpath(os.path.join(env.prefix().ROOT, pkg1._get_install_dir_dest()))
    )
    assert "foo.txt" in list_dir("")


def test_local_vfs(setup):
    """
    Tests that sorting the config files works properly
    """
    # Setup local mod
    test_local_package = os.path.join(env.prefix().LOCAL_MODS, "test_package")
    os.makedirs(test_local_package)

    sort_vfs()

    pkg1 = load_installed_pkg(Atom("test/test-1.0"))
    pkg2 = load_installed_pkg(Atom("test/test2"))
    assert pkg1 and pkg2
    path1 = os.path.normpath(
        os.path.join(env.prefix().ROOT, pkg1._get_install_dir_dest())
    )
    path2 = os.path.normpath(
        os.path.join(env.prefix().ROOT, pkg2._get_install_dir_dest())
    )

    # Check that config is correct
    lines = get_vfs_dirs()
    assert path1 in lines
    assert path2 in lines
    assert test_local_package in lines


@pytest.mark.skipif(
    sys.platform == "win32", reason="requires zipinfo command from unzip"
)
def test_archives(setup):
    """
    Tests that list_archive and extract_archive_file perform as expected
    """
    os.chdir(env.TMP_DIR)
    path = "test_file"
    archive_path = os.path.join(env.TMP_DIR, "test_archive.zip")
    with open(path, "w") as file:
        print("foo", file=file)
    with ZipFile(archive_path, "w") as myzip:
        myzip.write(path)

    assert path in list_archive(archive_path)
    extracted_path = extract_archive_file_to_tmp(archive_path, path)
    assert filecmp.cmp(path, extracted_path)
    os.remove(path)
    os.remove(archive_path)
    _cleanup_tmp_archive_dir()


def test_remove_vfs(setup):
    # Remove mods
    configure(["test/test-1.0", "test/test2-1.0"], no_confirm=True)

    pkg1 = load_installed_pkg(Atom("test/test"))
    pkg2 = load_installed_pkg(Atom("test/test2"))
    assert pkg1 and pkg2
    path1 = os.path.normpath(
        os.path.join(env.prefix().ROOT, pkg1._get_install_dir_dest())
    )
    path2 = os.path.normpath(
        os.path.join(env.prefix().ROOT, pkg2._get_install_dir_dest())
    )

    # Remove mods
    configure(["test/test-1.0", "test/test2-1.0"], no_confirm=True, depclean=True)

    # Check that config is no longer contains their entries
    lines = get_vfs_dirs()
    assert path1 not in lines
    assert path2 not in lines
