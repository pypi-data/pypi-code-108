# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pymosp']

package_data = \
{'': ['*']}

install_requires = \
['mypy>=0.931,<0.932',
 'requests>=2.25.1,<3.0.0',
 'types-requests>=2.27.5,<3.0.0']

entry_points = \
{'console_scripts': ['pymosp = bin.pymosp:main']}

setup_kwargs = {
    'name': 'pymosp',
    'version': '0.5.0',
    'description': 'Python Library to access MOSP.',
    'long_description': '# PyMOSP\n\n[![Latest release](https://img.shields.io/github/release/CASES-LU/PyMOSP.svg?style=flat-square)](https://github.com/CASES-LU/PyMOSP/releases/latest)\n[![License](https://img.shields.io/github/license/CASES-LU/PyMOSP.svg?style=flat-square)](https://www.gnu.org/licenses/agpl-3.0.html)\n[![Workflow](https://github.com/CASES-LU/PyMOSP/workflows/Python%20application/badge.svg?style=flat-square)](https://github.com/CASES-LU/PyMOSP/actions?query=workflow%3A%22Python+application%22)\n[![PyPi version](https://img.shields.io/pypi/v/pymosp.svg?style=flat-square)](https://pypi.org/project/pymosp)\n\n\nPyMOSP is a Python library to access [MOSP](https://github.com/CASES-LU/MOSP).\n\n\n## Installation\n\n### Use it as a command line tool\n\n```bash\n$ pipx install pymosp\ninstalled package pymosp 0.5.0, Python 3.10.2\nThese apps are now globally available\n  - pymosp\ndone! ✨ 🌟 ✨\n\n$ export MOSP_URL_API=https://objects.monarc.lu/api/v2/\n$ export TOKEN=<YOUR-TOKEN>\n\n$ pymosp object --list\n{\'metadata\': {\'count\': \'5074\', \'offset\': \'0\', \'limit\': \'10\'}, \'data\': [{\'id\': 144, \'name\': \'Use of an obsolete version of the messaging server\', \'description\': \'\', \'schema_id\': 14, \'org_id\': 4, \'last_updated\': \'2021-03-16T12:45:35.046659\', \'json_object\': {\'code\': \'1118\', \'uuid\': \'69fc03a0-4591-11e9-9173-0800277f0571\', \'label\': \'Use of an obsolete version of the messaging server\', \'language\': \'EN\', \'description\': \'\'}, \'organization\': {\'id\': 4, \'name\': \'MONARC\', \'description\': \'MONARC is a tool and a method allowing an optimised, precise and repeatable risk assessment.\', \'organization_type\': \'Non-Profit\', \'is_membership_restricted\': True, \'last_updated\': \'2018-05-18T09:50:57\'}, \'licences\': None},  ... ,  {\'id\': 284, \'name\': \'Tempting equipment (trading value, technology, strategic)\', \'description\': \'\', \'schema_id\': 14, \'org_id\': 4, \'last_updated\': \'2021-03-16T12:45:33.862787\', \'json_object\': {\'code\': \'278\', \'uuid\': \'69fc0ee2-4591-11e9-9173-0800277f0571\', \'label\': \'Tempting equipment (trading value, technology, strategic)\', \'language\': \'EN\', \'description\': \'\'}, \'organization\': {\'id\': 4, \'name\': \'MONARC\', \'description\': \'MONARC is a tool and a method allowing an optimised, precise and repeatable risk assessment.\', \'organization_type\': \'Non-Profit\', \'is_membership_restricted\': True, \'last_updated\': \'2018-05-18T09:50:57\'}, \'licences\': None}]}\n```\n\n### Use it as a Python library\n\n```bash\npip install pymosp\n```\n\n```python\nimport pymosp, os\nmosp = pymosp.PyMOSP(os.getenv("MOSP_URL_API"), os.getenv("TOKEN"))\nparams = {"organization": "MONARC", "schema": "Library objects"}\nr = mosp.objects(params=params)\nprint(r)\n```\n\n\nor via the Git repository:\n\n```bash\n$ git clone https://github.com/CASES-LU/PyMOSP\n$ cd PyMOSP\n$ poetry install\n$ poetry run nose2 -v --pretty-assert\n```\n\n\n## Examples\n\nSee the examples in the file [example.py](example.py) or in the tests folder.\n\n\n## License\n\nThis software is licensed under\n[GNU General Public License version 3](https://www.gnu.org/licenses/gpl-3.0.html).\n\n* Copyright (C) 2019-2022 Cédric Bonhomme\n* Copyright (C) 2019-2022 SECURITYMADEIN.LU\n\nFor more information, [the list of authors and contributors](AUTHORS.md)\nis available.\n',
    'author': 'Cédric Bonhomme',
    'author_email': 'cedric@cedricbonhomme.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/CASES-LU/PyMOSP',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
