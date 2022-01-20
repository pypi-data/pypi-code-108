# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['svante']

package_data = \
{'': ['*']}

install_requires = \
['Pint',
 'attrs',
 'colorama',
 'loguru',
 'matplotlib',
 'numpy',
 'pandas',
 'pydove',
 'schema',
 'scipy',
 'shellingham',
 'statsdict',
 'tabulate',
 'toml',
 'typer',
 'uncertainties']

entry_points = \
{'console_scripts': ['svante = svante.__main__:main']}

setup_kwargs = {
    'name': 'svante',
    'version': '0.3.2',
    'description': 'Configurable Arrhenius plots with uncertainties and ratios',
    'long_description': '=======================\nSvante: Arrhenius Plots\n=======================\n.. badges-begin\n\n| |PyPi| |Python Version| |Repo| |Downloads| |Dlrate|\n| |License| |Tests| |Coverage| |Codacy| |Issues| |Health|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/svante.svg\n   :target: https://pypi.org/project/svante/\n   :alt: PyPI package\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/svante\n   :target: https://pypi.org/project/svante\n   :alt: Supported Python Versions\n.. |Repo| image:: https://img.shields.io/github/last-commit/hydrationdynamics/svante\n    :target: https://github.com/hydrationdynamics/svante\n    :alt: GitHub repository\n.. |Downloads| image:: https://pepy.tech/badge/svante\n     :target: https://pepy.tech/project/svante\n     :alt: Download stats\n.. |Dlrate| image:: https://img.shields.io/pypi/dm/svante\n   :target: https://github.com/hydrationdynamics/svante\n   :alt: PYPI download rate\n.. |License| image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg\n    :target: https://github.com/hydrationdynamics/svante/blob/master/LICENSE.txt\n    :alt: License terms\n.. |Tests| image:: https://github.com/hydrationdynamics/svante/workflows/Tests/badge.svg\n   :target: https://github.com/hydrationdynamics/svante/actions?workflow=Tests\n   :alt: Tests\n.. |Coverage| image:: https://codecov.io/gh/hydrationdynamics/svante/branch/main/graph/badge.svg\n    :target: https://codecov.io/gh/hydrationdynamics/svante\n    :alt: Codecov.io test coverage\n.. |Codacy| image:: https://app.codacy.com/project/badge/Grade/4f45fe0d26104a6d86cb35404aa61e77\n   :target: https://www.codacy.com/gh/hydrationdynamics/svante/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=hydrationdynamics/svante&amp;utm_campaign=Badge_Grade\n    :alt: Codacy.io grade\n.. |Issues| image:: https://img.shields.io/github/issues/hydrationdynamics/svante.svg\n    :target:  https://github.com/hydrationdynamics/svante/issues\n    :alt: Issues reported\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/svante/latest.svg?label=Read%20the%20Docs\n   :target: https://svante.readthedocs.io/\n   :alt: Read the documentation at https://svante.readthedocs.io/\n.. |Health| image:: https://snyk.io/advisor/python/svante/badge.svg\n  :target: https://snyk.io/advisor/python/svante\n  :alt: Snyk health\n\n.. badges-end\n\n.. image:: https://raw.githubusercontent.com/hydrationdynamics/svante/main/docs/_static/logo.png\n   :target: https://raw.githubusercontent.com/hydrationdynamics/svante/main/LICENSE.artwork.txt\n   :alt: Fly Svante logo\n\n.. |Codecov| image:: https://codecov.io/gh/hydrationdynamics/svante/branch/main/graph/badge.svg\n   :target: https://codecov.io/gh/hydrationdynamics/svante\n   :alt: Codecov\n\nFeatures\n--------\n\n* Combines rates from multiple input `TSV files`_ using `pandas`_\n* Handles `uncertainties`_ in rates and temperatures\n* Creates `Arrhenius plots`_ using `Matplotlib`_\n* Fits activation enthalpies and prefactors to rates\n* Optionally, plots ratios of two rates\n\n\nRequirements\n------------\n\n* Tested on Python 3.9 and 3.10 on Linux and Mac\n\n\nInstallation\n------------\n\nYou can install *Svante* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install svante\n\n\nUsage\n-----\n\nPlease see the `Command-line Reference <Usage_>`_ for details.\n\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the `BSD 3-Clause license`_,\n*Svante* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\nSvante was written by Joel Berendzen.\n\n\n.. _TSV files: https://en.wikipedia.org/wiki/Tab-separated_values\n.. _pandas: https://pandas.pydata.org/\n.. _uncertainties: https://uncertainties-python-package.readthedocs.io/en/latest/user_guide.html\n.. _Arrhenius plots: https://en.wikipedia.org/wiki/Arrhenius_plot\n.. _Matplotlib: https://matplotlib.org/\n.. _BSD 3-Clause license: https://opensource.org/licenses/BSD-3-Clause\n.. _PyPI: https://pypi.org/\n.. _file an issue: https://github.com/joelb123/svante/issues\n.. _pip: https://pip.pypa.io/\n.. github-only\n.. _Contributor Guide: CONTRIBUTING.rst\n.. _Usage: https://svante.readthedocs.io/en/latest/usage.html\n',
    'author': 'Joel Berendzen',
    'author_email': 'joel@generisbio.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hydrationdynamics/svante',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.0,<3.11',
}


setup(**setup_kwargs)
