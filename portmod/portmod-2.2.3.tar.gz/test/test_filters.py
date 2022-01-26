# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
BLACKLIST and WHITELIST tests
"""

import os
import shutil
import zipfile

import pytest

from portmod.globals import env
from portmod.loader import load_file
from portmod.package import install_pkg
from portmod.repo import Repo
from portmodlib.fs import get_hash

from .env import setup_env, tear_down_env
from .test_loader import TMP_REPO, create_pybuild

LISTED = set(
    map(
        os.path.normpath,  # type:  ignore
        ["directory/foo.txt", "directory/bar.txt", "directory/bar.png"],
    )
)
OTHER = set(map(os.path.normpath, ["foo.txt", "directory/bar.gif"]))  # type:  ignore


@pytest.fixture(autouse=True)
def setup():
    """
    Sets up and tears down the test environment
    """
    dictionary = setup_env("test")
    env.REPOS.append(Repo("test", TMP_REPO))
    yield dictionary
    tear_down_env()
    shutil.rmtree(TMP_REPO)


def create_zip():
    """Creates test zip file"""
    os.chdir(env.TMP_DIR)
    os.makedirs(env.DOWNLOAD_DIR, exist_ok=True)
    get_hash.cache_clear()
    if not os.path.exists(os.path.join(env.DOWNLOAD_DIR, "test.zip")):
        with zipfile.ZipFile(os.path.join(env.DOWNLOAD_DIR, "test.zip"), "w") as myzip:
            for file in LISTED | OTHER:
                if os.path.dirname(file):
                    os.makedirs(os.path.dirname(file), exist_ok=True)
                with open(file, "w") as filep:
                    print("", file=filep)
                myzip.write(file, file)  # type:  ignore


def test_whitelist(setup):
    """
    Tests that InstallDir whitelisting works properly
    """
    pybuild = """
import os
import sys
from pybuild import Pybuild1, InstallDir

class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"
    SRC_URI="test.zip"

    INSTALL_DIRS=[
        InstallDir(".", WHITELIST=["directory/*.txt", "directory/*.png", "*.jpg"]),
    ]
    """
    create_zip()
    file = create_pybuild(pybuild, manifest=True)
    mod = load_file(file)
    install_pkg(mod, set())

    base = os.path.join(env.prefix().ROOT, mod._get_install_dir_dest())
    whitelisted = LISTED.copy()
    for root, _, files in os.walk(base):
        for file in files:
            path = os.path.relpath(root, base)
            fullpath = os.path.normpath(os.path.join(path, file))
            if fullpath in whitelisted:
                whitelisted.discard(fullpath)  # type:  ignore
            else:
                raise Exception(f"File {fullpath} is not in the whitelist!")

    # Only the whitelisted file can be present
    assert not whitelisted


def test_blacklist(setup):
    """
    Tests that InstallDir blacklisting works properly
    """
    pybuild = """
import os
import sys
from pybuild import Pybuild1, InstallDir

class Package(Pybuild1):
    NAME="Test"
    DESC="Test"
    LICENSE="GPL-3"
    SRC_URI="test.zip"

    INSTALL_DIRS=[
        InstallDir(".", BLACKLIST=["directory/*.txt", "directory/*.png", "*.jpg"]),
    ]
    """
    create_zip()
    file = create_pybuild(pybuild, manifest=True)
    mod = load_file(file)
    install_pkg(mod, set())

    other_files = OTHER.copy()

    base = os.path.join(env.prefix().ROOT, mod._get_install_dir_dest())
    for root, _, files in os.walk(base):
        for file in files:
            path = os.path.relpath(root, base)
            fullpath = os.path.normpath(os.path.join(path, file))
            if fullpath in LISTED:
                raise Exception(f"File {fullpath} is in the black!")
            if fullpath in other_files:
                other_files.discard(fullpath)  # type:  ignore

    assert not other_files
