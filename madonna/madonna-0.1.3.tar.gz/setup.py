# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['madonna']

package_data = \
{'': ['*']}

extras_require = \
{':python_version < "3.8"': ['typing-extensions>=3.10.0.2,<4.0.0.0']}

setup_kwargs = {
    'name': 'madonna',
    'version': '0.1.3',
    'description': 'Python semver parsing library.',
    'long_description': '# Madonna\n\n[![License](https://img.shields.io/github/license/FollowTheProcess/madonna)](https://github.com/FollowTheProcess/madonna)\n[![PyPI](https://img.shields.io/pypi/v/madonna.svg?logo=python)](https://pypi.python.org/pypi/madonna)\n[![GitHub](https://img.shields.io/github/v/release/FollowTheProcess/madonna?logo=github&sort=semver)](https://github.com/FollowTheProcess/madonna)\n[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/FollowTheProcess/madonna)\n[![CI](https://github.com/FollowTheProcess/madonna/workflows/CI/badge.svg)](https://github.com/FollowTheProcess/madonna/actions?query=workflow%3ACI)\n[![Coverage](https://github.com/FollowTheProcess/madonna/raw/main/docs/img/coverage.svg)](https://github.com/FollowTheProcess/madonna)\n\n**A Python semver parsing library.**\n\n* Free software: MIT License\n\n* Documentation: [https://FollowTheProcess.github.io/madonna/](<https://FollowTheProcess.github.io/madonna/>)\n\n## Project Description\n\nMadonna is a small, simple [semver] utility library with support for parsing, writing, and otherwise interacting with semantic versions in code.\n\n**Why the stupid name?**\n\nGet it? "Like a Version"... 👏🏻\n\nAlso naming things on PyPI is hard!\n\n## Installation\n\n```shell\npip install madonna\n```\n\n## Quickstart\n\nThe only construct in madonna is the `Version` object, you can use it for all sorts of useful things...\n\n### Create a New Version\n\n```python\nfrom madonna import Version\n\nv = Version(major=1, minor=2, patch=4)\n```\n\n### Parse a Version from a string\n\n```python\nfrom madonna import Version\n\nVersion.from_string("v1.2.4-rc.1+build.123")\n# Version(major=1, minor=2, patch=4, prerelease="rc.1", buildmetadata="build.123")\n```\n\n### Or JSON\n\n```python\nfrom madonna import Version\n\nVersion.from_json(\'{"major": 1, "minor": 2, "patch": 4}\')\n```\n\nAnd you can also dump a `Version` to a variety of formats too!\n\n## Contributing\n\n`madonna` is an open source project and, as such, welcomes contributions of all kinds :smiley:\n\nYour best bet is to check out the [contributing guide] in the docs!\n\n### Credits\n\nThis package was created with [cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [FollowTheProcess/cookie_pypackage] project template.\n\n[cookiecutter]: https://github.com/cookiecutter/cookiecutter\n[FollowTheProcess/cookie_pypackage]: https://github.com/FollowTheProcess/cookie_pypackage\n[contributing guide]: https://FollowTheProcess.github.io/madonna/contributing/contributing.html\n[semver]: https://semver.org\n',
    'author': 'Tom Fleet',
    'author_email': 'tomfleet2018@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/FollowTheProcess/madonna',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
