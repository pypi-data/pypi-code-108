# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pygemstones',
 'pygemstones.io',
 'pygemstones.system',
 'pygemstones.type',
 'pygemstones.util',
 'pygemstones.vendor']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.20.10,<2.0.0', 'colorama>=0.4.4,<0.5.0']

setup_kwargs = {
    'name': 'pygemstones',
    'version': '0.0.9',
    'description': 'Python package that group a lot of classes and functions that help software development.',
    'long_description': '<p align="center">\n    <a href="https://github.com/paulo-coutinho/pygemstones" target="_blank" rel="noopener noreferrer">\n        <img width="120" src="extras/images/logo.png" alt="PyGemstones Logo">\n    </a>\n</p>\n\n<h1 align="center">Python Gemstones</h1>\n\n<p align="center">\n  <a href="https://github.com/paulo-coutinho/pygemstones/actions"><img src="https://github.com/paulo-coutinho/pygemstones/actions/workflows/build.yml/badge.svg" alt="Build Status"></a>\n  <a href="https://codecov.io/github/paulo-coutinho/pygemstones?branch=main"><img src="https://img.shields.io/codecov/c/github/paulo-coutinho/pygemstones/main.svg?sanitize=true" alt="Coverage Status"></a>\n</p>\n\n<p align="center">\nPython package that group a lot of classes and functions that help software development.\n</p>\n\n<br>\n\n### Requirements\n\n* Python 3.6+\n\n### How To Use\n\nTo use in your project, install `pygemstones` module:\n\n```\npip install pygemstones\n```\n\nor:\n\n```\npoetry add pygemstones\n```\n\nAnd before call any pygemstones module, import system boostrap and call `init` method:\n\n```python\nfrom pygemstones.system import bootstrap\nbootstrap.init()\n```\n\n### Modules\n\nThere are several implemented modules for you to use:\n\n- io.file\n- io.net\n- io.pack\n- system.bootstrap\n- system.platform\n- system.runner\n- system.settings\n- type.list\n- type.string\n- util.log\n- vendor.aws\n\n### Development\n\nThese are the requirements for local development:\n\n* Python 3.6+\n* Poetry (https://python-poetry.org/)\n\nYou can install locally:\n\n```\npoetry install\n```\n\nOr can build and generate a package:\n\n```\npoetry build\n```\n\n### Tests\n\n```\npoetry run pytest\n```\n\n### Coverage Tests\n\n```\npoetry run pytest --cov=pygemstones --cov-report=html tests\n```\n\nNote: see coverage report in htmlcov/index.html\n\n### Linters\n\nTo run all linters use:\n\n```\npoetry run black --check pygemstones/\npoetry run black --check tests/\npoetry run mypy --ignore-missing-imports pygemstones/\npoetry run mypy --ignore-missing-imports tests/\n```\n\n### Build and Publish\n\nTo build the package use:\n\n```\npoetry build\n```\n\nSet the token from your PyPI account with:\n\n```\npoetry config pypi-token.pypi [PyPI-Api-Access-Token]\n```\n\nAnd publish with:\n\n```\npoetry publish --build\n```\n\n### Release\n\nTo create a release for Github Action `publish steps` create a tag and push. Example:\n\n```\ngit tag v0.0.1\ngit push origin v0.0.1\n```\n\nAfter release action finish, publish the release on Github `releases` page and Github Action will run `publish steps` automatically.\n',
    'author': 'Paulo Coutinho',
    'author_email': 'paulo@prsolucoes.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/paulo-coutinho/pygemstones',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
