# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ncdump_rich']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0', 'netCDF4>=1.5.7,<2.0.0', 'rich>=10.7,<12.0']

entry_points = \
{'console_scripts': ['ncdump-rich = ncdump_rich.__main__:main']}

setup_kwargs = {
    'name': 'ncdump-rich',
    'version': '0.1.5',
    'description': 'Rich NcDump',
    'long_description': 'Rich NcDump\n===========\n\n|PyPI| |Status| |Python Version| |License|\n\n|Read the Docs| |Tests| |Codecov|\n\n|pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/ncdump-rich.svg\n   :target: https://pypi.org/project/ncdump-rich/\n   :alt: PyPI\n.. |Status| image:: https://img.shields.io/pypi/status/ncdump-rich.svg\n   :target: https://pypi.org/project/ncdump-rich/\n   :alt: Status\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/ncdump-rich\n   :target: https://pypi.org/project/ncdump-rich\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/pypi/l/ncdump-rich\n   :target: https://opensource.org/licenses/GPL-3.0\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/ncdump-rich/latest.svg?label=Read%20the%20Docs\n   :target: https://ncdump-rich.readthedocs.io/\n   :alt: Read the documentation at https://ncdump-rich.readthedocs.io/\n.. |Tests| image:: https://github.com/engeir/ncdump-rich/workflows/Tests/badge.svg\n   :target: https://github.com/engeir/ncdump-rich/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://img.shields.io/codecov/c/gh/engeir/ncdump-rich?label=codecov&logo=codecov\n   :target: https://codecov.io/gh/engeir/ncdump-rich\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\n\nFeatures\n--------\n\nThis project provides an easy way of previewing ``netCDF`` files with nicely\nformatted text in your terminal. The information extracted from the ``.nc``\nfiles are obtained in a similar way to `this example`_, with some\nmodifications. The source code used on the website can be downloaded as\n``netcdf_example.py`` with:\n\n.. code:: console\n\n   $ curl -O http://schubert.atmos.colostate.edu/~cslocum/code/netcdf_example.py\n\nTo make the output more readable it is formatted using the python library rich_.\n\n\nRequirements\n------------\n\nThe project depends on the python packages ``click``, ``netCDF4`` and ``rich``. Installation via\npip_ or pipx_ ensures that all dependencies are installed correctly.\n\n\nInstallation\n------------\n\nYou can install *Rich NcDump* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install ncdump-rich\n\nor perhaps even better via pipx_:\n\n.. code:: console\n\n   $ pipx install ncdump-rich\n\n\nUsage\n-----\n\nPlease see the `Command-line Reference <Usage_>`_ for details.\n\nExamples\n^^^^^^^^\n\nUse the program as a previewer for ``.nc`` files, for example through stpv_. `My own\nfork`_ provides additional support for previewing ``.nc`` files using this project.\n\nPreview in lf_\n\n.. image:: ../demo/lf-demo.png\n   :width: 600\n\nSimilarly you can get preview of ``.nc`` files in nnn_ by including an option for the\nextension ``nc`` in the |preview-tui plugin|_.\n\n.. code:: console\n\n   nc) fifo_pager ncdump-rich -i "$1" ;;\n\nPreview in nnn_\n\n.. image:: ../demo/nnn-demo.png\n   :width: 600\n\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the `GPL 3.0 license`_,\n*Rich NcDump* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\nThis project was generated from `@cjolowicz`_\'s `Hypermodern Python Cookiecutter`_ template.\n\n.. _@cjolowicz: https://github.com/cjolowicz\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _GPL 3.0 license: https://opensource.org/licenses/GPL-3.0\n.. _PyPI: https://pypi.org/\n.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _file an issue: https://github.com/engeir/ncdump-rich/issues\n.. _pip: https://pip.pypa.io/\n.. _pipx: https://github.com/pypa/pipx\n.. _stpv: https://github.com/Naheel-Azawy/stpv\n.. _My own fork: https://github.com/engeir/stpv\n.. _rich: https://rich.readthedocs.io/en/latest/\n.. _this example: http://schubert.atmos.colostate.edu/~cslocum/netcdf_example.html\n.. _nnn: https://github.com/jarun/nnn\n.. _lf: https://github.com/gokcehan/lf\n.. |preview-tui plugin| replace:: ``preview-tui`` plugin\n.. _preview-tui plugin: https://github.com/jarun/nnn/blob/fc00faf7d0f4cd0b4637e719af52100861e8c17a/plugins/preview-tui#L247\n.. github-only\n.. _Contributor Guide: CONTRIBUTING.rst\n.. _Usage: https://ncdump-rich.readthedocs.io/en/latest/usage.html\n',
    'author': 'Eirik Enger',
    'author_email': 'eirroleng@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/engeir/ncdump-rich',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
