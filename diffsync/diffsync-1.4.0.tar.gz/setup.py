# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['diffsync']

package_data = \
{'': ['*']}

extras_require = \
{':(python_version >= "3.6" and python_version < "3.7") and (extra == "docs")': ['dataclasses>=0.7,<0.8'],
 ':extra == "docs"': ['pydantic>=1.7.4,<2.0.0,!=1.8,!=1.8.1',
                      'structlog>=20.1.0,<22.0.0'],
 'docs': ['colorama>=0.4.3,<0.5.0',
          'sphinx>=4.0.2,<5.0.0',
          'm2r2>=0.2.7,<0.3.0',
          'sphinx-rtd-theme>=0.5.2,<0.6.0',
          'toml>=0.10.2,<0.11.0']}

setup_kwargs = {
    'name': 'diffsync',
    'version': '1.4.0',
    'description': 'Library to easily sync/diff/update 2 different data sources',
    'long_description': '# DiffSync\n\nDiffSync is a utility library that can be used to compare and synchronize different datasets.\n\nFor example, it can be used to compare a list of devices from 2 inventory systems and, if required, synchronize them in either direction.\n\n```python\nA = DiffSyncSystemA()\nB = DiffSyncSystemB()\n\nA.load()\nB.load()\n\n# Show the difference between both systems, that is, what would change if we applied changes from System B to System A\ndiff_a_b = A.diff_from(B)\nprint(diff_a_b.str())\n\n# Update System A to align with the current status of system B\nA.sync_from(B)\n\n# Update System B to align with the current status of system A\nA.sync_to(B)\n```\n\n> You may wish to peruse the `diffsync` [GitHub topic](https://github.com/topics/diffsync) for examples of projects using this library.\n\n# Documentation\n\nThe documentation is available [on Read The Docs](https://diffsync.readthedocs.io/en/latest/index.html).\n\n# Installation\n\n### Option 1: Install from PyPI.\n\n```\n$ pip install diffsync\n```\n\n### Option 2: Install from a GitHub branch, such as main as shown below.\n```\n$ pip install git+https://github.com/networktocode/diffsync.git@main\n```\n\n# Contributing\nPull requests are welcomed and automatically built and tested against multiple versions of Python through GitHub Actions.\n\nThe project is following Network to Code software development guidelines and are leveraging the following:\n\n- Black, Pylint, Bandit, flake8, and pydocstyle for Python linting and formatting.\n- pytest, coverage, and unittest for unit tests.\n\n# Questions\nPlease see the [documentation](https://diffsync.readthedocs.io/en/latest/index.html) for detailed documentation on how to use `diffsync`. For any additional questions or comments, feel free to swing by the [Network to Code slack channel](https://networktocode.slack.com/) (channel #networktocode). Sign up [here](http://slack.networktocode.com/)',
    'author': 'Network to Code, LLC',
    'author_email': 'info@networktocode.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://diffsync.readthedocs.io',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
