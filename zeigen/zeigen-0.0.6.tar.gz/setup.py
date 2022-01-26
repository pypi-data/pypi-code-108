# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zeigen']

package_data = \
{'': ['*']}

install_requires = \
['Pint',
 'attrs',
 'colorama',
 'gemmi',
 'loguru',
 'matplotlib',
 'numpy',
 'pandas',
 'rcsbsearch',
 'schema',
 'scipy',
 'statsdict',
 'tabulate',
 'toml',
 'typer',
 'types-tabulate',
 'types-toml',
 'uncertainties']

entry_points = \
{'console_scripts': ['zeigen = zeigen.__main__:main']}

setup_kwargs = {
    'name': 'zeigen',
    'version': '0.0.6',
    'description': 'Find hydrated waters in atomic-resolution crystal structures',
    'long_description': '============================\nZeigen: Find Hydrated Waters\n============================\n.. badges-begin\n\n| |PyPi| |Python Version| |Repo| |Downloads| |Dlrate|\n| |License| |Tests| |Coverage| |Codacy| |Issues| |Health|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/zeigen.svg\n   :target: https://pypi.org/project/zeigen/\n   :alt: PyPI package\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/zeigen\n   :target: https://pypi.org/project/zeigen\n   :alt: Supported Python Versions\n.. |Repo| image:: https://img.shields.io/github/last-commit/hydrationdynamics/zeigen\n    :target: https://github.com/hydrationdynamics/zeigen\n    :alt: GitHub repository\n.. |Downloads| image:: https://pepy.tech/badge/zeigen\n     :target: https://pepy.tech/project/zeigen\n     :alt: Download stats\n.. |Dlrate| image:: https://img.shields.io/pypi/dm/zeigen\n   :target: https://github.com/hydrationdynamics/zeigen\n   :alt: PYPI download rate\n.. |License| image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg\n    :target: https://github.com/hydrationdynamics/zeigen/blob/master/LICENSE.txt\n    :alt: License terms\n.. |Tests| image:: https://github.com/hydrationdynamics/zeigen/workflows/Tests/badge.svg\n   :target: https://github.com/hydrationdynamics/zeigen/actions?workflow=Tests\n   :alt: Tests\n.. |Coverage| image:: https://codecov.io/gh/hydrationdynamics/zeigen/branch/main/graph/badge.svg\n    :target: https://codecov.io/gh/hydrationdynamics/zeigen\n    :alt: Codecov.io test coverage\n.. |Codacy| image:: https://app.codacy.com/project/badge/Grade/3e29ba5ba23d48888372138790ab26f3\n    :target: https://www.codacy.com/gh/hydrationdynamics/zeigen?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=hydrationdynamics/zeigen&amp;utm_campaign=Badge_Grade\n    :alt: Codacy.io grade\n.. |Issues| image:: https://img.shields.io/github/issues/hydrationdynamics/zeigen.svg\n    :target:  https://github.com/hydrationdynamics/zeigen/issues\n    :alt: Issues reported\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/zeigen/latest.svg?label=Read%20the%20Docs\n   :target: https://zeigen.readthedocs.io/\n   :alt: Read the documentation at https://zeigen.readthedocs.io/\n.. |Health| image:: https://snyk.io/advisor/python/zeigen/badge.svg\n  :target: https://snyk.io/advisor/python/zeigen\n  :alt: Snyk health\n\n.. badges-end\n\n.. image:: https://raw.githubusercontent.com/hydrationdynamics/zeigen/main/docs/_static/logo.png\n   :target: https://raw.githubusercontent.com/hydrationdynamics/zeigen/main/LICENSE.artwork.txt\n   :alt: Fly Zeigen logo\n\n.. |Codecov| image:: https://codecov.io/gh/hydrationdynamics/zeigen/branch/main/graph/badge.svg\n   :target: https://codecov.io/gh/hydrationdynamics/zeigen\n   :alt: Codecov\n\nFeatures\n--------\n\n* Finds protonated waters in atomic-resolution structures\n\n\nRequirements\n------------\n\n* Tested on Python 3.9 and 3.10 on Linux and Mac\n\n\nInstallation\n------------\n\nYou can install *Zeigen* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install zeigen\n\n\nUsage\n-----\n\nPlease see the `Command-line Reference <Usage_>`_ for details.\n\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the `BSD 3-Clause license`_,\n*Zeigen* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\nZeigen was written by Joel Berendzen.\n\n\n.. _pandas: https://pandas.pydata.org/\n.. _uncertainties: https://uncertainties-python-package.readthedocs.io/en/latest/user_guide.html\n.. _Arrhenius plots: https://en.wikipedia.org/wiki/Arrhenius_plot\n.. _BSD 3-Clause license: https://opensource.org/licenses/BSD-3-Clause\n.. _PyPI: https://pypi.org/\n.. _file an issue: https://github.com/joelb123/zeigen/issues\n.. _pip: https://pip.pypa.io/\n.. github-only\n.. _Contributor Guide: CONTRIBUTING.rst\n.. _Usage: https://zeigen.readthedocs.io/en/latest/usage.html\n',
    'author': 'Joel Berendzen',
    'author_email': 'joel@generisbio.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hydrationdynamics/zeigen',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.1,<3.11',
}


setup(**setup_kwargs)
