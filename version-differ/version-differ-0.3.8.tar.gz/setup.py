# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['version_differ']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.24,<4.0.0',
 'PyYAML>=5.4.1,<6.0.0',
 'click>=8.0.0,<9.0.0',
 'pygit2>=1.7.2,<2.0.0',
 'requests>=2.26.0,<3.0.0',
 'rich>=10.3.0,<11.0.0',
 'unidiff>=0.7.0,<0.8.0',
 'urllib3>=1.26.7,<2.0.0']

entry_points = \
{'console_scripts': ['version-differ = version_differ.__main__:main']}

setup_kwargs = {
    'name': 'version-differ',
    'version': '0.3.8',
    'description': 'Accurate diffing between two versions of a project',
    'long_description': 'version-differ\n===========================\n\n|PyPI| |Python Version| |License| |Read the Docs| |Build| |Tests| |Codecov| |pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/version-differ.svg\n   :target: https://pypi.org/project/version-differ/\n   :alt: PyPI\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/version-differ\n   :target: https://pypi.org/project/version-differ\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/github/license/nasifimtiazohi/version-differ\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/version-differ/latest.svg?label=Read%20the%20Docs\n   :target: https://version-differ.readthedocs.io/\n   :alt: Read the documentation at https://version-differ.readthedocs.io/\n.. |Build| image:: https://github.com/nasifimtiazohi/version-differ/workflows/Build%20version-differ%20Package/badge.svg\n   :target: https://github.com/nasifimtiazohi/version-differ/actions?workflow=Package\n   :alt: Build Package Status\n.. |Tests| image:: https://github.com/nasifimtiazohi/version-differ/workflows/Run%20version-differ%20Tests/badge.svg\n   :target: https://github.com/nasifimtiazohi/version-differ/actions?workflow=Tests\n   :alt: Run Tests Status\n.. |Codecov| image:: https://codecov.io/gh/nasifimtiazohi/version-differ/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/nasifimtiazohi/version-differ\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\n\nFeatures\n--------\n\n* Given any two versions of a package, returns the list of changed files with the count of loc_added and loc_removed in each file.\n\n* Covers eight ecosystems, namely Cargo, Composer, Go, Maven, npm, NuGet, pip, and RubyGems.\n\n* For Cargo, Composer, Maven, npm, pip, and RubyGems, version-differ downloads source code for a version of a package directly from the respective package registries to measure the diff.\n\n* For Go and NuGet, it clones the source code repository, applies some heuristics to detect package specific files, and measures the diff.\n\n* diffing is performed using native git-diff, ignores black lines (does not ignore comments).\n\n\n\nInstallation\n------------\n\nYou can install *version-differ* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install version-differ\n\n\nUsage\n-----\n\nPlease see the `Command-line Reference <Usage_>`_ for details.\n\n\nCredits\n-------\n\nThis package was created with cookietemple_ using Cookiecutter_ based on Hypermodern_Python_Cookiecutter_.\n\n.. _cookietemple: https://cookietemple.com\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _PyPI: https://pypi.org/\n.. _Hypermodern_Python_Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _pip: https://pip.pypa.io/\n.. _Usage: https://version-differ.readthedocs.io/en/latest/usage.html\n',
    'author': 'Nasif Imtiaz',
    'author_email': 'nasifimtiaz88@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nasifimtiazohi/version-differ',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
