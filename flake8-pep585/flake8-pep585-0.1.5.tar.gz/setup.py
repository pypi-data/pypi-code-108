# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flake8_pep585']

package_data = \
{'': ['*']}

entry_points = \
{'flake8.extension': ['PEA = flake8_pep585.plugin:Pep585Plugin']}

setup_kwargs = {
    'name': 'flake8-pep585',
    'version': '0.1.5',
    'description': 'flake8 plugin to enforce new-style type hints (PEP 585)',
    'long_description': '# flake8-pep585\n\nThis plugin enforces the changes proposed by PEP 585.\n\n```py\nfrom typing import Callable\n# PEA001 typing.Callable is deprecated, use collections.abc.Callable instead. See PEP 585 for details\n\nimport typing as ty\nty.Match\n# PEA001 typing.Match is deprecated, use re.Match instead. See PEP 585 for details\n```\n',
    'author': 'decorator-factory',
    'author_email': 'decorator-factory@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/decorator-factory/flake8-pep585',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
