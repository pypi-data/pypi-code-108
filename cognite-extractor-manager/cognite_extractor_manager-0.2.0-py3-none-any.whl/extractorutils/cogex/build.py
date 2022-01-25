#  Copyright 2020 Cognite AS
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import fileinput
import os
import re
from argparse import Namespace
from time import time
from typing import Dict, List

import toml

from cognite.extractorutils.cogex.io import errorprint, headerprint, lineprint

_spec_template = """
# -*- mode: python ; coding: utf-8 -*-

import os
import sys

try:
    from {package} import __version__
    version = f"{{__version__}}-"
except ImportError:
    version = ""

if os.name == "nt":
    script_path = "{script_path_win}"

else:
    script_path = "{script_path_unix}"


a = Analysis(
    [script_path],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=f"{name}-{{version}}{{sys.platform}}",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    #icon="logo.ico",
)
"""


def update_version(initfile: str) -> None:
    print(f"Updating {initfile}")

    init_version_search = re.search(r'^__version__\s*=\s*"(.*)"', open(initfile).read(), re.M)
    if init_version_search is None:
        print("No __version__ found")
        return

    init_version = init_version_search.group(1)
    print(f"Version in {initfile}: {init_version}")

    poetry_version = toml.load("pyproject.toml")["tool"]["poetry"]["version"]
    print(f"Version in pyproject.toml: {poetry_version}")

    if poetry_version == init_version:
        print("No updating necessary")
        return

    print("Changing __version__ to match pyproject")
    with fileinput.input(initfile, inplace=True) as file:
        for line in file:
            print(line.replace(init_version, poetry_version), end="")


def build(args: Namespace) -> None:
    start_time = time()

    pyproject = toml.load("pyproject.toml")

    # Ensure spec file exists
    if args.spec is None:
        # No spec file, attempt to create one on-the-fly
        headerprint("Generating spec files")
        os.makedirs("build", exist_ok=True)
        specfiles = generate_spec(keep_spec=False)

    else:
        specfiles = args.spec

    # Make sure __version__ is updated if present
    headerprint("Updating __version__ in __init__.py from pyproject.toml")
    try:
        packages = [
            os.path.join(package["from"], package["include"]) for package in pyproject["tool"]["poetry"]["packages"]
        ]
    except KeyError:
        packages = [pyproject["tool"]["poetry"]["name"]]

    for package in packages:
        for dirpath, dirnames, filenames in os.walk(package):
            for filename in filenames:
                if filename == "__init__.py":
                    update_version(os.path.join(dirpath, filename))

    headerprint("Making sure Poetry environment is up to date")
    os.system("poetry install")

    # Build executables
    s = "s" if len(specfiles) > 1 else ""
    headerprint(f"Building executable{s}")
    for specfile in specfiles:
        if os.system(f"poetry run pyinstaller {specfile}"):
            lineprint("red")
            errorprint(f"Build of {specfile} failed")
            print()
            return

    lineprint()
    headerprint("Build done")

    print(f"Resulting file{s} found in ./dist")
    print(f"Total build time: {time() - start_time:.1f} s")
    print()


def generate_spec(keep_spec: bool = True) -> List[str]:
    pyproject = toml.load("pyproject.toml")

    path_prefix = "build" + os.path.sep if not keep_spec else ""

    try:
        scripts: Dict[str, str] = pyproject["tool"]["poetry"]["scripts"]

    except KeyError:
        print("No scripts found in pyprojects.toml")
        name = input("What is the name of the program to build? ")
        module = input("What is the runnable module to build? ")
        scripts = {name: module}

    files = []

    for name in scripts:
        path_parts = scripts[name].split(":")[0].split(".")
        package = ".".join(path_parts[0:-1])

        if not keep_spec:
            path_parts.insert(0, "..")

        win_path = r"\\".join(path_parts) + ".py"
        unix_path = "/".join(path_parts) + ".py"

        print(f"Generating {path_prefix}{name}.spec")
        with open(f"{path_prefix}{name}.spec", "w") as specfile:
            specfile.write(
                _spec_template.format(name=name, script_path_win=win_path, script_path_unix=unix_path, package=package)
            )

        files.append(f"{path_prefix}{name}.spec")

    return files
