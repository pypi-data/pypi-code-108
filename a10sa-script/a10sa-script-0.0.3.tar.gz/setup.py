# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['a10sa_script', 'a10sa_script.command', 'a10sa_script.script']

package_data = \
{'': ['*']}

install_requires = \
['buttplug>=0.2.1,<0.3.0',
 'click>=8.0.1',
 'loguru>=0.5.3,<0.6.0',
 'sortedcontainers>=2.4.0,<3.0.0',
 'typing-extensions>=4.0.1,<5.0.0']

entry_points = \
{'console_scripts': ['a10sa-script = a10sa_script.__main__:main']}

setup_kwargs = {
    'name': 'a10sa-script',
    'version': '0.0.3',
    'description': 'A10SA Script',
    'long_description': 'A10SA Script\n============\n\n|PyPI| |Status| |Python Version| |License|\n\n|Read the Docs| |Tests| |Codecov|\n\n|pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/a10sa-script.svg\n   :target: https://pypi.org/project/a10sa-script/\n   :alt: PyPI\n.. |Status| image:: https://img.shields.io/pypi/status/a10sa-script.svg\n   :target: https://pypi.org/project/a10sa-script/\n   :alt: Status\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/a10sa-script\n   :target: https://pypi.org/project/a10sa-script\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/pypi/l/a10sa-script\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/a10sa-script/latest.svg?label=Read%20the%20Docs\n   :target: https://a10sa-script.readthedocs.io/\n   :alt: Read the documentation at https://a10sa-script.readthedocs.io/\n.. |Tests| image:: https://github.com/bhrevol/a10sa-script/workflows/Tests/badge.svg\n   :target: https://github.com/bhrevol/a10sa-script/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/bhrevol/a10sa-script/branch/main/graph/badge.svg\n   :target: https://app.codecov.io/gh/bhrevol/a10sa-script\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\nLibrary for manipulating Vorze A10 sex toy scripts.\n\n\nFeatures\n--------\n\n* Read/Write/Convert supported script formats.\n* Export scripts as `Buttplug Protocol`_ command sequences.\n\n.. _Buttplug Protocol: https://buttplug.io/\n\nSupported Formats\n-----------------\n\n* Vorze CSV\n* Afesta/LPEG VCSX (``.bin``)\n\n\nRequirements\n------------\n\n* Python 3.8+\n\n\nInstallation\n------------\n\nYou can install *A10SA Script* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install a10sa-script\n\n\nUsage\n-----\n\nConvert VCSX ``Vorze_CycloneSA.bin`` to ``script_cyclone.csv``:\n\n.. code:: py\n\n    >>> from a10sa_script.script import VCSXCycloneScript, VorzeRotateScript\n    >>> with open("Vorze_CycloneSA.bin", "rb") as f:\n    ...     vcsx = VCSXCycloneScript.load(f)\n    >>> with open("script_cyclone.csv", "wb") as f:\n    ...     VorzeRotateScript(vcsx.commands).dump(f)\n\nPlease see the `Command-line Reference <Usage_>`_ for details.\n\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the `MIT license`_,\n*A10SA Script* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\nThis project was generated from `@cjolowicz`_\'s `Hypermodern Python Cookiecutter`_ template.\n\n.. _@cjolowicz: https://github.com/cjolowicz\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _MIT license: https://opensource.org/licenses/MIT\n.. _PyPI: https://pypi.org/\n.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _file an issue: https://github.com/bhrevol/a10sa-script/issues\n.. _pip: https://pip.pypa.io/\n.. github-only\n.. _Contributor Guide: https://a10sa-script.readthedocs.io/en/latest/contributing.html\n.. _Usage: https://a10sa-script.readthedocs.io/en/latest/usage.html\n',
    'author': 'byeonhyeok',
    'author_email': 'bhrevol@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bhrevol/a10sa-script',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
