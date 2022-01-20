# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['statsdict']

package_data = \
{'': ['*']}

install_requires = \
['Pint', 'attrs', 'loguru', 'tabulate', 'typer', 'uncertainties']

entry_points = \
{'console_scripts': ['statsdict = statsdict.__main__:main']}

setup_kwargs = {
    'name': 'statsdict',
    'version': '0.1.5',
    'description': 'Saveable dictionary of global stats',
    'long_description': '=========================\nStatsDict: Save Run Stats\n=========================\n.. badges-begin\n\n| |PyPi| |Python Version| |Repo| |Downloads| |Dlrate|\n| |License| |Tests| |Coverage| |Codacy| |Issues| |Health|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/statsdict.svg\n   :target: https://pypi.org/project/statsdict/\n   :alt: PyPI package\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/statsdict\n   :target: https://pypi.org/project/statsdict\n   :alt: Supported Python Versions\n.. |Repo| image:: https://img.shields.io/github/last-commit/hydrationdynamics/statsdict\n    :target: https://github.com/hydrationdynamics/statsdict\n    :alt: GitHub repository\n.. |Downloads| image:: https://pepy.tech/badge/statsdict\n     :target: https://pepy.tech/project/statsdict\n     :alt: Download stats\n.. |Dlrate| image:: https://img.shields.io/pypi/dm/statsdict\n   :target: https://github.com/hydrationdynamics/statsdict\n   :alt: PYPI download rate\n.. |License| image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg\n    :target: https://github.com/hydrationdynamics/statsdict/blob/master/LICENSE.txt\n    :alt: License terms\n.. |Tests| image:: https://github.com/hydrationdynamics/statsdict/workflows/Tests/badge.svg\n   :target: https://github.com/hydrationdynamics/statsdict/actions?workflow=Tests\n   :alt: Tests\n.. |Coverage| image:: https://codecov.io/gh/hydrationdynamics/statsdict/branch/main/graph/badge.svg\n    :target: https://codecov.io/gh/hydrationdynamics/statsdict\n    :alt: Codecov.io test coverage\n.. |Codacy| image:: https://app.codacy.com/project/badge/Grade/b27a34201f26408f96e5e33664cb7655\n    :target: https://www.codacy.com/gh/hydrationdynamics/statsdict/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=hydrationdynamics/statsdict&amp;utm_campaign=Badge_Grade\n    :alt: Codacy.io grade\n.. |Issues| image:: https://img.shields.io/github/issues/hydrationdynamics/statsdict.svg\n    :target:  https://github.com/hydrationdynamics/statsdict/issues\n    :alt: Issues reported\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/statsdict/latest.svg?label=Read%20the%20Docs\n   :target: https://statsdict.readthedocs.io/\n   :alt: Read the documentation at https://statsdict.readthedocs.io/\n.. |Health| image:: https://snyk.io/advisor/python/statsdict/badge.svg\n  :target: https://snyk.io/advisor/python/statsdict\n  :alt: Snyk health\n\n.. badges-end\n\n.. image:: https://raw.githubusercontent.com/hydrationdynamics/statsdict/main/docs/_static/logo.png\n   :target: https://raw.githubusercontent.com/hydrationdynamics/statsdict/main/LICENSE.artwork.txt\n   :alt: Fly StatsDict logo\n\n.. |Codecov| image:: https://codecov.io/gh/hydrationdynamics/statsdict/branch/main/graph/badge.svg\n   :target: https://codecov.io/gh/hydrationdynamics/statsdict\n   :alt: Codecov\n\nFeatures\n--------\n\n* Save global run statistics to a JSON file suitable for use with a web service.\n\n\nRequirements\n------------\n\n* Tested on Python 3.8 to 3.10 on Linux and Mac\n\n\nInstallation\n------------\n\nYou can install *StatsDict* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install statsdict\n\n\nUsage\n-----\n\nPlease see the `Command-line Reference <Usage_>`_ for details.\n\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the `BSD 3-Clause license`_,\n*StatsDict* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\nStatsDict was written by Joel Berendzen.\n\n\n.. _BSD 3-Clause license: https://opensource.org/licenses/BSD-3-Clause\n.. _PyPI: https://pypi.org/\n.. _file an issue: https://github.com/joelb123/statsdict/issues\n.. _pip: https://pip.pypa.io/\n.. github-only\n.. _Contributor Guide: CONTRIBUTING.rst\n.. _Usage: https://statsdict.readthedocs.io/en/latest/usage.html\n',
    'author': 'Joel Berendzen',
    'author_email': 'joel@generisbio.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hydrationdynamics/statsdict',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.0,<4.0.0',
}


setup(**setup_kwargs)
