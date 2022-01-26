# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
from logging import error, warning

from portmod.globals import env
from portmod.loader import load_installed_pkg
from portmod.parsers.manifest import ManifestEntry
from portmodlib.atom import Atom
from portmodlib.l10n import l10n


def get_packages(path: str):
    for category in os.listdir(path):
        if os.path.isdir(os.path.join(path, category)) and not category.startswith("."):
            for package in os.listdir(os.path.join(path, category)):
                if os.path.isdir(os.path.join(path, category, package)):
                    yield category, package


def validate(args):
    # Check that mods in the DB correspond to mods in the mods directory
    for category, package in get_packages(env.prefix().INSTALLED_DB):
        # Check that pybuild can be loaded
        pkg = load_installed_pkg(Atom(f"{category}/{package}"))
        if not pkg:
            error(
                l10n(
                    "in-database-could-not-load",
                    atom=Atom(f"{category}/{package}"),
                )
            )
        else:
            # Check files listed in CONTENTS
            for path, entry in pkg.get_contents().entries.items():
                realpath = os.path.join(env.prefix().ROOT, path)
                if not os.path.exists(realpath):
                    warning(l10n("installed-file-missing", path=path))
                elif entry != ManifestEntry.from_path(entry.filetype, realpath, path):
                    warning(l10n("installed-file-mismatch", path=path, pkg=pkg.CPN))
