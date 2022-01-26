# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

from coveriteam.language import CoVeriLangException
import os
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo
import re
import urllib.request
import requests
from pathlib import Path
import shutil
import sys
from typing import Dict, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from coveriteam.language.artifact import Artifact

LOG_DIR = Path.cwd() / "cvt-output"
TOOL_OUTPUT_FILE = "output.txt"
INPUT_FILE_DIR = f'{Path(__file__).parent.resolve() / "artifactlibrary/"}/'
ACTOR_CONFIG_PATH = ""
USE_PYTHON_PROCESSES = False
CURRENTLY_IN_MPI = False

CVT_DEBUG_LEVEL = 15


def set_cache_directories(d=None):
    global INSTALL_DIR, ARCHIVE_DOWNLOAD_PATH, TOOL_INFO_DOWNLOAD_PATH
    if d:
        cache_dir = d
    elif os.getenv("XDG_CACHE_HOME"):
        cache_dir = Path(os.getenv("XDG_CACHE_HOME")) / "coveriteam"
    else:
        cache_dir = Path.home() / ".cache" / "coveriteam"
    INSTALL_DIR = cache_dir / "tools"
    ARCHIVE_DOWNLOAD_PATH = cache_dir / "archives"
    TOOL_INFO_DOWNLOAD_PATH = cache_dir / "toolinfocache"
    sys.path.append(str(TOOL_INFO_DOWNLOAD_PATH))
    create_cache_directories()


def set_cache_update(flag):
    global UPDATE_CACHE
    UPDATE_CACHE = flag


def set_python_processes_flag(flag):
    global USE_PYTHON_PROCESSES
    if flag:
        USE_PYTHON_PROCESSES = True
    else:
        USE_PYTHON_PROCESSES = False


def create_cache_directories():
    # Create directories and set path.
    if not ARCHIVE_DOWNLOAD_PATH.is_dir():
        ARCHIVE_DOWNLOAD_PATH.mkdir(parents=True)
    if not TOOL_INFO_DOWNLOAD_PATH.is_dir():
        TOOL_INFO_DOWNLOAD_PATH.mkdir(parents=True)

    if not INSTALL_DIR.is_dir():
        INSTALL_DIR.mkdir(parents=True)


def get_INSTALL_DIR():
    return INSTALL_DIR


def get_ARCHIVE_DOWNLOAD_PATH():
    return ARCHIVE_DOWNLOAD_PATH


def get_TOOL_INFO_DOWNLOAD_PATH():
    return TOOL_INFO_DOWNLOAD_PATH


def is_url(path_or_url):
    return "://" in path_or_url or path_or_url.startswith("file:")


def make_url(path_or_url):
    """Make a URL from a string which is either a URL or a local path,
    by adding "file:" if necessary.
    """
    if not is_url(path_or_url):
        return "file:" + urllib.request.pathname2url(path_or_url)
    return path_or_url


def download_if_needed(location, target):
    url = make_url(location)
    headers = {"User-Agent": "Mozilla"}
    etag_path = Path(str(target) + ".etag")
    if etag_path.is_file() and target.is_file():
        etag = etag_path.open("r").read()
        headers["If-None-Match"] = etag

    try:
        response = requests.get(url, allow_redirects=True, headers=headers)
        if response.status_code == 304:
            return False
        if response.status_code != 200:
            msg = (
                "Couldn't download tool archive from: %s. Server returned the code: %s"
                % (str(url), response.status_code)
            )
            raise CoVeriLangException(msg)
        with target.open("wb") as out_file:
            out_file.write(response.content)
        # write the eta tag
        try:
            etag = response.headers["etag"]
            with Path(str(target) + ".etag").open("w") as f:
                f.write(etag)
        except KeyError:
            pass  # no etag to cache
        return True
    except requests.ConnectionError:
        print("No network access. Running in offline mode.")
        return False


def create_archive(dirname, archive_path):
    with ZipFile(archive_path, "w", ZIP_DEFLATED) as zipf:
        for root, _dirs, files in os.walk(dirname):
            for f in files:
                filepath = os.path.join(root, f)
                zipf.write(filepath, os.path.relpath(filepath, dirname))


def unzip(archive, target_dir):
    if target_dir.is_dir():
        shutil.rmtree(target_dir)

    with ZipFile(archive, "r") as zipfile:
        top_folder = INSTALL_DIR / zipfile.filelist[0].filename.split("/")[0]
        # Not to use extract all as it does not preserves the permission for executable files.
        # See: https://bugs.python.org/issue15795
        # See https://stackoverflow.com/questions/39296101/python-zipfile-removes-execute-permissions-from-binaries
        for member in zipfile.namelist():
            if not isinstance(member, ZipInfo):
                member = zipfile.getinfo(member)
            extracted_file = zipfile.extract(member, INSTALL_DIR)
            # This takes first two bytes from four bytes.
            attr = member.external_attr >> 16
            if attr != 0:
                os.chmod(extracted_file, attr)
        top_folder.rename(target_dir)


def filter_dict(d, keys_to_keep):
    """Filters the first dict by the keys given as second parameter."""
    return {k: d[k] for k in d if k in keys_to_keep}


def complete_outputs(
    provided_outputs: Dict[str, "Artifact"],
    expected_outputs: Dict[str, Type["Artifact"]],
) -> Dict[str, "Artifact"]:
    """Returns a dictionary with all expected outputs. Outputs not provided by provided_outputs are initialized with the neutral version of each artifact type."""
    return {
        k: provided_outputs[k] if k in provided_outputs else expected_outputs[k]()
        for k in expected_outputs
    }


def str_dict(d):
    return {k: str(d[k]) for k in d.keys()}


def dict_clash(d1, d2):
    """
    This function checks if there is a key present in both dictionaries
    whose values are different.
    """
    for k in d1.keys():
        if k in d2.keys() and d1[k] != d2[k]:
            return True

    return False


def rename_dict(d, renaming_map):
    return {(renaming_map.get(k, None) or k): d[k] for k in d.keys()}


def collect_variables(exp):
    regex_isinstance = r"(?<=isinstance\()\S+(?=,)"
    regex_in = r"\w+(?= in \[)"
    regex = regex_isinstance + "|" + regex_in
    names = re.findall(regex, exp)

    return names


def get_additional_paths_for_container_config():
    base_dir = Path(__file__).parent.parent.resolve()
    paths = [str(base_dir / "lib"), str(base_dir / "coveriteam" / "toolconfigs")]
    return paths
