# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['depdive']

package_data = \
{'': ['*']}

install_requires = \
['PyGithub>=1.55,<2.0',
 'PyYAML>=5.4.1,<6.0.0',
 'click>=8.0.0,<9.0.0',
 'package-locator>=0.4.2,<0.5.0',
 'rich>=10.3.0,<11.0.0',
 'version-differ>=0.3.3,<0.4.0']

entry_points = \
{'console_scripts': ['depdive = depdive.__main__:main']}

setup_kwargs = {
    'name': 'depdive',
    'version': '0.0.27',
    'description': 'Performs security checks for a dependency update',
    'long_description': 'depdive\n===========================\n\n|PyPI| |Python Version| |License| |Read the Docs| |Build| |Tests| |Codecov| |pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/depdive.svg\n   :target: https://pypi.org/project/depdive/\n   :alt: PyPI\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/depdive\n   :target: https://pypi.org/project/depdive\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/github/license/nasifimtiazohi/depdive\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/depdive/latest.svg?label=Read%20the%20Docs\n   :target: https://depdive.readthedocs.io/\n   :alt: Read the documentation at https://depdive.readthedocs.io/\n.. |Build| image:: https://github.com/nasifimtiazohi/depdive/workflows/Build%20depdive%20Package/badge.svg\n   :target: https://github.com/nasifimtiazohi/depdive/actions?workflow=Package\n   :alt: Build Package Status\n.. |Tests| image:: https://github.com/nasifimtiazohi/depdive/workflows/Run%20depdive%20Tests/badge.svg\n   :target: https://github.com/nasifimtiazohi/depdive/actions?workflow=Tests\n   :alt: Run Tests Status\n.. |Codecov| image:: https://codecov.io/gh/nasifimtiazohi/depdive/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/nasifimtiazohi/depdive\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\n\nFeatures\n--------\n\n* TODO\n\n\nInstallation\n------------\n\nYou can install *depdive* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install depdive\n\n\nUsage\n-----\n\nPlease see the `Command-line Reference <Usage_>`_ for details.\n\n\nCredits\n-------\n\nThis package was created with cookietemple_ using Cookiecutter_ based on Hypermodern_Python_Cookiecutter_.\n\n.. _cookietemple: https://cookietemple.com\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _PyPI: https://pypi.org/\n.. _Hypermodern_Python_Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _pip: https://pip.pypa.io/\n.. _Usage: https://depdive.readthedocs.io/en/latest/usage.html\n',
    'author': 'Nasif Imtiaz',
    'author_email': 'nasifimtiaz88@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nasifimtiazohi/depdive',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
