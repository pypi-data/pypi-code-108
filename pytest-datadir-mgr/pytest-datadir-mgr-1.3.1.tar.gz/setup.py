# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytest_datadir_mgr']

package_data = \
{'': ['*']}

install_requires = \
['progressbar2', 'pytest', 'requests_download']

entry_points = \
{'pytest11': ['datadir_mgr = pytest_datadir_mgr']}

setup_kwargs = {
    'name': 'pytest-datadir-mgr',
    'version': '1.3.1',
    'description': 'Manager for test data: downloads, artifact caching, and a tmpdir context.',
    'long_description': '=============================\ndatadir-mgr plugin for pytest\n=============================\n.. badges-begin\n\n| |pypi| |Python Version| |repo| |downloads| |dlrate|\n| |license|  |build| |coverage| |codacy| |issues|\n\n.. |pypi| image:: https://img.shields.io/pypi/v/pytest-datadir-mgr.svg\n    :target: https://pypi.python.org/pypi/pytest-datadir-mgr\n    :alt: Python package\n\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/pytest-datadir-mgr\n   :target: https://pypi.python.org/pypi/pytest-datadir-mgr\n   :alt: Supported Python Versions\n\n.. |repo| image:: https://img.shields.io/github/last-commit/joelb123/pytest-datadir-mgr\n    :target: https://github.com/joelb123/pytest-datadir-mgr\n    :alt: GitHub repository\n\n.. |downloads| image:: https://pepy.tech/badge/pytest-datadir-mgr\n     :target: https://pepy.tech/project/pytest_datadir_mgr\n     :alt: Download stats\n\n.. |dlrate| image:: https://img.shields.io/pypi/dm/pytest-datadir-mgr\n   :target: https://github.com/joelb123/pytest-datadir-mgr\n   :alt: PYPI download rate\n\n.. |license| image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg\n    :target: https://github.com/joelb123/pytest-datadir-mgr/blob/master/LICENSE.txt\n    :alt: License terms\n\n.. |build| image:: https://github.com/joelb123/pytest-datadir-mgr/workflows/tests/badge.svg\n    :target:  https://github.com/joelb123/pytest-datadir-mgr.actions\n    :alt: GitHub Actions\n\n.. |codacy| image:: https://api.codacy.com/project/badge/Grade/f306c40d604f4e62b8731ada896d8eb2\n    :target: https://www.codacy.com/gh/joelb123/pytest-datadir-mgr?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=joelb123/pytest-datadir-mgr&amp;utm_campaign=Badge_Grade\n    :alt: Codacy.io grade\n\n.. |coverage| image:: https://codecov.io/gh/joelb123/pytest-datadir-mgr/branch/master/graph/badge.svg\n    :target: https://codecov.io/gh/joelb123/pytest-datadir-mgr\n    :alt: Codecov.io test coverage\n\n.. |issues| image:: https://img.shields.io/github/issues/joelb123/pytest-datadir-mgr.svg\n    :target:  https://github.com/joelb123/pytest-datadir-mgr/issues\n    :alt: Issues reported\n\n.. badges-end\n\n.. image:: https://raw.githubusercontent.com/joelb123/pytest-datadir-mgr/main/docs/_static/logo.png\n   :target: https://raw.githubusercontent.com/joelb123/pytest-datadir-mgr/main/LICENSE.artwork.txt\n   :alt: Logo credit Jørgen Stamp, published under a Creative Commons Attribution 2.5 Denmark License.\n\nThe ``datadir-mgr`` plugin for pytest_ provides the ``datadir_mgr`` fixture which\nallow test functions to easily download data files and cache generated data files\nin data directories in a manner that allows for overlaying of results. ``datadir-mgr``\nis pathlib-based, so complete paths to data files are handled,\nnot just filenames.\n\n\n\nThis plugin behaves like a limited dictionary, with ``datadir_mgr[item]`` returning a path\nwith the most specific scope (out of ``global, module, [class], [function]`` that matches\nthe string or path specified by ``item``.  In addition to serving data files already stored\nin the data directory, the fixture provides five methods useful for adding to the test data\nstored in the repository:\n\n- The ``download`` method allows downloading data files into data directories, with\n  option MD5 checksum checks, un-gzipping, and a progressbar.\n- The ``savepath`` fixture lets an arbitrary path relative to the current working\n  directory to be saved at a particular scope in the data directories.\n- The ``add_scope`` method lets one add directories from scopes different from\n  the present request to be added to the search path.  This lets the results\n  of previous cached steps to be used in scopes other than global.\n- The ``in_tmp_dir`` method creates a context in a temporary directory with\n  a list of request file paths copied in.  Optionally, all output file paths\n  can be saved at a particular scope at cleanup with an optional exclusion\n  filter pattern (e.g., for excluding log files).  Note that files in directories\n  that begin with ``test_`` or end with ``_test`` could be confused with\n  scope directories and cannnot be saved.  If ``progressbar`` is set to "True",\n  then the progress of file copying will be shown, which is helpful in some long-running\n  pytest jobs, e.g. on Travis.\n- The ``paths_from_scope`` returns a list of all paths to files from a specified scope.\n\n\nPrerequisites\n-------------\nPython 3.6 or greater is required.  This package is tested under Linux, MacOS, and Windows\nusing Python 3.9.\n\n.. _pytest: http://pytest.org/\n',
    'author': 'Joel Berendzen',
    'author_email': 'joel@generisbio.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/joelb123/pytest-datadir-mgr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
