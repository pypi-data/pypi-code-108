#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Subpackage used to display the versions of all dependencies."""
import importlib
import locale
import os
import platform
import struct
import sys
import typing as t

from ._version import get_versions

__all__ = ["show_versions"]


def get_system_info() -> t.Mapping[str, t.Any]:
    """Get extra informations."""
    # Get git commit hash
    commit = get_versions()["full-revisionid"]  # type: t.Optional[str]
    version = get_versions()["version"]  # type: str

    size_integer = struct.calcsize("P")  # type: int
    language_code, encoding = locale.getlocale()

    return {
        "commit": commit,
        "version": version,
        "python": sys.version,
        "python-bits": size_integer * 8,
        "OS": platform.system(),
        "OS-release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "byteorder": sys.byteorder,
        "LC_ALL": os.environ.get("LC_ALL"),
        "LANG": os.environ.get("LANG"),
        "LOCALE": f"{language_code}.{encoding}",
    }


def show_versions():
    """Display the versions of Pyxel and its dependencies.

    Examples
    --------
    >>> import pyxel
    >>> pyxel.show_versions()
    INSTALLED VERSIONS
    ------------------
    commit     : cfb7ce2886d24f884699aafd1ad7dc6f8615252d
    version    : 0.6+18.gcfb7ce2.dirty
    python     : 3.8.5 | packaged by conda-forge | (default, Aug 29 2020, 01:18:42)
    [Clang 10.0.1 ]
    python-bits: 64
    OS         : Darwin
    OS-release : 19.5.0
    machine    : x86_64
    processor  : i386
    byteorder  : little
    LC_ALL     : None
    LANG       : None
    LOCALE     : None.UTF-8
    pyxel      : 0.6+18.gcfb7ce2.dirty
    astropy    : 4.0.1.post1
    dask       : 2.25.0
    distributed: 2.25.0
    h5py       : 2.10.0
    ipywidgets : 7.5.1
    jupyter    : installed
    jupyterlab : 2.2.7
    matplotlib : 3.3.1
    numba      : 0.51.2
    numpy      : 1.19.1
    pandas     : 1.1.2
    poppy      : 0.9.1
    pygmo      : 2.15.0
    scipy      : 1.5.2
    setuptools : 49.6.0.post20200814
    pip        : 20.2.3
    conda      : 4.8.4
    black      : 20.8b1
    flake8     : 3.8.3
    isort      : 5.5.2
    mypy       : installed
    pytest     : 6.0.1
    sphinx     : None
    """
    system_info = get_system_info()  # type: t.Mapping[str, t.Any]

    dependencies_lst = (
        "pyxel",
        # required
        "astropy",
        "bokeh",
        "cloudpickle",
        "dask",
        "dask_jobqueue",
        "distributed",
        "fsspec",
        "h5py",
        "holoviews",
        "ipywidgets",
        "jupyter",
        "jupyterlab",
        "matplotlib",
        "notebook",
        "numba",
        "numpy",
        "pandas",
        "PIL",
        "poppy",
        "pygmo",
        "pympler",
        "scipy",
        "seaborn",
        "skimage",
        "tqdm",
        "typing-extensions",
        "yaml",
        "xarray",
        "xlrd",
        "openpyxl",
        "netcdf4",
        # Install / build
        "setuptools",
        "pip",
        "conda",
        # Test
        "black",
        "blackdoc",
        "flake8",
        "isort",
        "mypy",
        "pytest",
        "tox",
        # Docs
        "sphinx",
    )  # type: t.Tuple[str, ...]

    dependencies = {}  # type: dict

    for module_name in dependencies_lst:
        try:
            # Try to get a module
            module = importlib.import_module(module_name)
        except Exception:
            dependencies[module_name] = None
        else:
            try:
                # Try to get a version
                version = module.__version__  # type: ignore
                dependencies[module_name] = version
            except Exception:
                dependencies[module_name] = "installed"

    max_length = max(map(len, [*system_info, *dependencies]))
    print("")
    print("INSTALLED VERSIONS")
    print("------------------")
    for key, value in system_info.items():
        print(f"{key:<{max_length}}: {value}")
    print("")
    for key, value in dependencies.items():
        print(f"{key:<{max_length}}: {value}")
