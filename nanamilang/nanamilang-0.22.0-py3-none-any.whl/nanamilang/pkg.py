"""NanamiLang Package Manager API"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

import os
import urllib.request


def pkg_remote_path(pkg: str) -> str:
    """NanamiLang Package Manager API, remote pkg path"""

    return f'https://nanamilang.jedi2light.moe/pkg/{pkg}.nml'


def ensure_module_local_path(pkg: str) -> str:
    """NanamiLang Package Manager API, ensure local pkg path"""

    home = os.path.join(os.environ.get('XDG_DATA_HOME',
                                       os.environ.get('LOCALAPPDATA')), 'nanamilang')

    if not os.path.exists(home):
        os.mkdir(home)

    return os.path.join(home, f'{pkg}.nml')


def populate_nanamilang_package(pkg: str) -> bool:
    """NanamiLang Package Manager API, populate NanamiLang package from remote to local"""

    return bool(urllib.request.urlretrieve(pkg_remote_path(pkg), ensure_module_local_path(pkg)))
