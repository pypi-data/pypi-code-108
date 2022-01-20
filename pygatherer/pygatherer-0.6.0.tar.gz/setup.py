# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pygatherer', 'pygatherer.utils']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.0.0,<5.0.0',
 'lxml>=4.0.0,<5.0.0',
 'pathurl>=0.5.0,<0.6.0',
 'requests>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'pygatherer',
    'version': '0.6.0',
    'description': 'An API for the gatherer',
    'long_description': '==================================================\npygatherer: unofficial python API for the gatherer\n==================================================\n\n.. image:: https://github.com/spapanik/pygatherer/actions/workflows/build.yml/badge.svg\n  :alt: Build\n  :target: https://github.com/spapanik/pygatherer/actions/workflows/build.yml\n.. image:: https://img.shields.io/lgtm/alerts/g/spapanik/pygatherer.svg\n  :alt: Total alerts\n  :target: https://lgtm.com/projects/g/spapanik/pygatherer/alerts/\n.. image:: https://img.shields.io/github/license/spapanik/pygatherer\n  :alt: License\n  :target: https://github.com/spapanik/pygatherer/blob/main/LICENSE.txt\n.. image:: https://img.shields.io/pypi/v/pygatherer\n  :alt: PyPI\n  :target: https://pypi.org/project/pygatherer\n.. image:: https://pepy.tech/badge/pygatherer\n  :alt: Downloads\n  :target: https://pepy.tech/project/pygatherer\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n  :alt: Code style\n  :target: https://github.com/psf/black\n\n``pygatherer`` is an unofficial python API for the gatherer.\n\nIn a nutshell\n-------------\n\nInstallation\n^^^^^^^^^^^^\n\nThe easiest way is to use `poetry`_ to manage your dependencies and add *pygatherer* to them.\n\n.. code-block:: toml\n\n    [tool.poetry.dependencies]\n    pygatherer = "*"\n\nUsage\n^^^^^\n\n``pygatherer`` has a module named ``utils`` that contains all the relevant parsers.\n\nLinks\n-----\n\n- `Documentation`_\n- `Changelog`_\n\n\n.. _poetry: https://python-poetry.org/\n.. _Changelog: https://github.com/spapanik/pygatherer/blob/main/CHANGELOG.rst\n.. _Documentation: https://pygatherer.readthedocs.io/en/latest/\n',
    'author': 'Stephanos Kuma',
    'author_email': 'stephanos@kuma.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/spapanik/pygatherer',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
