# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['di', 'di._utils', 'di.api']

package_data = \
{'': ['*']}

install_requires = \
['anyio>=3,<4', 'graphlib2>=0.2.13']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=3'],
 ':python_version < "3.9"': ['typing-extensions>=3']}

setup_kwargs = {
    'name': 'di',
    'version': '0.51.0',
    'description': 'Autowiring dependency injection',
    'long_description': '# di: pythonic dependency injection\n\n[![codecov](https://codecov.io/gh/adriangb/di/branch/main/graph/badge.svg?token=A0FXC8B93Y)](https://codecov.io/gh/adriangb/di)\n![Workflow](https://github.com/adriangb/di/actions/workflows/workflow.yaml/badge.svg)\n[![di](https://snyk.io/advisor/python/di/badge.svg)](https://snyk.io/advisor/python/di)\n\n⚠️ This project is a WIP. Until there is a 1.X.Y release, expect breaking changes. ⚠️\n\nFor more information, see our [docs].\n\n[docs]: https://www.adriangb.com/di/\n\nSee this release on GitHub: [v0.51.0](https://github.com/adriangb/di/releases/tag/0.51.0)\n',
    'author': 'Adrian Garcia Badaracco',
    'author_email': 'adrian@adriangb.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/adriangb/di',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
