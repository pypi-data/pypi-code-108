from dataclasses import dataclass, field
from pathlib import Path
from typing import Type, AnyStr, List, Optional
from zipfile import ZipFile, ZIP_DEFLATED
import imghdr
import inspect
import json
import os
import pprint
import re
import shutil
import stat
import tempfile
import warnings

import pkg_resources
import requests

from chai_py.auth import get_auth
from chai_py.chai_bot import ChaiBot

MAX_SUPPORTED_MEMORY = 4096


@dataclass
class Metadata:
    """Information required for bot deployment."""
    # Name of the bot.
    name: str
    # Profile image for the bot. Has to be a valid URL.
    image_url: str
    # The alphanumeric part of a hex color code. (E.g. ffffff)
    color: str
    # Description of the bot.
    description: str
    # Python class (N.B. not object!) that inherits from ChaiBot.
    input_class: Type[ChaiBot]

    # Developer Unique ID.
    developer_uid: str = field(default_factory=lambda: get_auth().uid)

    # Total available memory for the bot in MB. This includes memory needed to store sources and data.
    memory: int = 256

    def verify(self, bot_file: Path):
        """Performs basic checks to ensure validity of the metadata."""
        assert isinstance(self.name, str)
        assert len(self.name) >= 3, "Bot name has to be at least 3 characters."

        assert len(self.description) > 0, "Bot has to have description."
        assert self.input_class.__init__ is ChaiBot.__init__, \
            "Do not override ChaiBot.__init__(). Override the setup() method instead."

        assert not (bot_file.parent / "main.py").exists(), "Do not create a main.py file in your bot's root directory."

        try:
            verify_image_url(self.image_url)
        except Exception:
            raise ValueError(f"Could not verify image url ({self.image_url})")

        assert isinstance(self.color, str)
        assert re.search(r"^(?:[0-9a-fA-F]{3}){1,2}$", self.color), \
            f"Color has to be provided as the alphanumeric part of the hex code (e.g. ffffff), found {self.color}"

        assert isinstance(self.memory, int), f"Attribute .memory has to be an integer (found type {type(self.memory)})."
        assert self.memory <= MAX_SUPPORTED_MEMORY, f"Attribute .memory has to be less than or equal to {MAX_SUPPORTED_MEMORY} (found {self.memory})."


def package(metadata: Metadata, requirements: Optional[List[str]] = None, path: Optional[str] = None):
    """Packages the chatbot into a single archive for deployment.

    Performs some preliminary checks on the metadata.
    Creates a _package.zip file in the directory containing the file that contains the bot class
    unless a path is provided.

    :param metadata:
    :param requirements:
    :param path:
    :return:
    """
    bot_file = Path(inspect.getfile(metadata.input_class))

    print("Running verification checks on metadata.")
    metadata.verify(bot_file)

    metadata_dict = {
        'name': metadata.name,
        'imageUrl': metadata.image_url,
        'color': metadata.color,
        'developerUid': metadata.developer_uid,
        'description': metadata.description,
        'inputFile': bot_file.stem,
        'inputClass': metadata.input_class.__name__,
        'memory': metadata.memory,
    }
    print("Prepared metadata:")
    pprint.pprint(metadata_dict)

    print("Preparing temporary directory...")
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy files in bot directory
        def ignore(src, names):
            ignore_list = []
            for name in names:
                # e.g .git folder is not wanted
                if name.startswith('.') or name.startswith('_package.zip'):
                    warnings.warn(
                        f"Ignoring files which start with '.': {name}.",
                        RuntimeWarning
                    )
                    ignore_list.append(name)
                if name == "main.py":
                    raise RuntimeError("Bot root directory cannot contain a main.py file.")
            return ignore_list

        copytree(bot_file.parent, temp_dir, ignore=ignore)
        # Write metadata.json
        with (Path(temp_dir) / "metadata.json").open("w") as f:
            json.dump(metadata_dict, f)

        # Write requirements.txt
        if requirements:
            write_valid_requirements_file(Path(temp_dir) / "requirements.txt", requirements)

        # Create zip
        if path is None:
            path = bot_file.parent / "_package.zip"
        else:
            path = Path(path)

        with path.open("wb") as f:
            zipfile_from_folder(temp_dir, f)
        print(f"Created zip package at {path}.")


def verify_image_url(url: str):
    """Verifies that the provided url resolves to an image.

    Performs a GET request on the given url and performs a trivial (non-conclusive) check
    that the image type can be inferred from the received bytes.

    :param url:
    :return:
    """
    r = requests.get(url)
    try:
        imghdr.what(None, h=r.content)
    except Exception:
        raise ValueError(
            f"Could not verify image type from bytes "
            f"(response content-type of {r.headers.get('content-type')})"
        )


def zipfile_from_folder(folder: AnyStr, file):
    # Adapted from https://stackoverflow.com/a/17080988
    with ZipFile(file, "w", compression=ZIP_DEFLATED) as zip_archive:
        for root, dirs, files in os.walk(folder):
            # add directory (needed for empty dirs)
            zip_archive.write(root, os.path.relpath(root, folder))
            for file in files:
                filename = os.path.join(root, file)
                if os.path.isfile(filename):  # regular files only
                    arcname = os.path.join(os.path.relpath(root, folder), file)
                    zip_archive.write(filename, arcname)


def copytree(src, dst, symlinks=False, ignore=None):
    """Copies files from src to dst.

    Taken from https://stackoverflow.com/a/22331852.
    Necessitated by Python 3.7 environment; Python 3.8's shutil.copytree can be used directly
    as it has the necessary dirs_exist_ok argument.

    :param src: Source directory
    :param dst: Target directory
    :param symlinks:
    :param ignore: Callable
    :return:
    """
    if not os.path.exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)
    lst = os.listdir(src)
    if ignore:
        excl = ignore(src, lst)
        lst = [x for x in lst if x not in excl]
    for item in lst:
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if symlinks and os.path.islink(s):
            if os.path.lexists(d):
                os.remove(d)
            os.symlink(os.readlink(s), d)
            try:
                st = os.lstat(s)
                mode = stat.S_IMODE(st.st_mode)
                os.lchmod(d, mode)
            except Exception:
                pass  # lchmod not available
        elif os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def write_valid_requirements_file(path: AnyStr, requirements: List[str]):
    """Writes a valid requirements.txt file.

    Iterates through list of requirements, writing valid entries to the specified file,
    Ignores (and prints) invalid requirements.

    :param path:
    :param requirements:
    :return:
    """
    with Path(path).open("w") as f:
        for requirement in requirements:
            try:
                pkg_resources.Requirement.parse(requirement)
                f.write(requirement + "\n")
            except Exception as e:
                print(f"Ignoring requirement {requirement}: {e}")
