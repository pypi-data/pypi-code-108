# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
import shutil
import sys
from functools import lru_cache
from typing import List
from zipfile import ZipFile

from portmodlib.execute import execute


class UnsupportedArchive(Exception):
    """
    Exception raised when encountering archive types that are not supported

    Supported archive types include zip and bsa
    """


def list_archive(file: str) -> List[str]:
    """
    Lists the contents of the given archive

    args:
        file: Path of the archive
    returns:
        List of the archive's contents
    raises:
        UnsupportedArchive: If the archive has no handler
    """
    _, ext = os.path.splitext(file)
    fmt_ext = ext.lstrip(".").lower()
    if fmt_ext == "zip":
        return zip_list(file)
    if fmt_ext == "bsa":
        return bsa_list(file)
    raise UnsupportedArchive(f"No handler available for extension {fmt_ext}")


def extract_archive_file(archive: str, file: str, output_dir: str):
    """
    Extracts the given file from the archive to the output_dir

    args:
        archive: Path of the archive
        file: Path of the file to be extracted relative to the root of the archive
        output_dir: Directory into which the file is to be extracted
    raises:
        UnsupportedArchive: If the archive has no handler
    """
    _, ext = os.path.splitext(archive)
    fmt_ext = ext.lstrip(".").lower()
    if fmt_ext == "zip":
        return zip_extract(archive, file, output_dir)
    if fmt_ext == "bsa":
        return bsa_extract(archive, file, output_dir)
    raise UnsupportedArchive(f"No handler available for extension {fmt_ext}")


def zip_list(archive: str) -> List[str]:
    """Lists the files in the given zip archive"""
    with ZipFile(archive) as file:
        return file.namelist()


def zip_extract(archive: str, file: str, output_dir: str):
    """Extracts the given file from the zip archive to the output_dir"""
    with ZipFile(archive) as zip_file:
        zip_file.extract(file, path=output_dir)


def bsa_list(archive: str) -> List[str]:
    """Lists the files in the given bsa archive"""
    return (
        (execute(f'{_bsatool_command()} list "{archive}" ', pipe_output=True) or "")
        .replace("\\", "/")
        .splitlines()
    )


def bsa_extract(archive: str, file: str, output_dir: str):
    """Extracts the given file from the bsa archive to the output_dir"""
    execute(f'{_bsatool_command()} extract "{archive}" "{file}" "{output_dir}"')


@lru_cache()
def _bsatool_command():
    if shutil.which("bsatool"):
        return "bsatool"

    if sys.platform == "win32":
        from winreg import HKEY_LOCAL_MACHINE  # pylint: disable=import-error

        from .winreg import read_reg

        openmw_installs = read_reg(
            HKEY_LOCAL_MACHINE, r"Software\Wow6432Node\OpenMW.org"
        )
        if openmw_installs:
            # Add the last install found in the key. This should correspond to the newest version.
            return os.path.join(next(reversed(openmw_installs.values())), "bsatool.exe")

    raise FileNotFoundError("Could not find bsatool executable!")
