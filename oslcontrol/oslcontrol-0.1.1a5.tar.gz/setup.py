# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oslcontrol']

package_data = \
{'': ['*']}

install_requires = \
['flexsea>=7.2.3,<8.0.0',
 'pyserial>=3.5,<4.0',
 'rich>=10.14,<12.0',
 'typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['oslcontrol = oslcontrol.__main__:app']}

setup_kwargs = {
    'name': 'oslcontrol',
    'version': '0.1.1a5',
    'description': 'An open-source software library for numerical computation, data acquisition, and control of lower-limb robotic prosthesis.',
    'long_description': '# oslcontrol\n\n<div align="center">\n\n[![Build status](https://github.com/imsenthur/oslcontrol/workflows/build/badge.svg?branch=master&event=push)](https://github.com/imsenthur/oslcontrol/actions?query=workflow%3Abuild)\n[![Python Version](https://img.shields.io/pypi/pyversions/oslcontrol.svg)](https://pypi.org/project/oslcontrol/)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/imsenthur/oslcontrol/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)\n[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/imsenthur/oslcontrol/blob/master/.pre-commit-config.yaml)\n[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/imsenthur/oslcontrol/releases)\n[![License](https://img.shields.io/github/license/imsenthur/oslcontrol)](https://github.com/imsenthur/oslcontrol/blob/master/LICENSE)\n![Coverage Report](assets/images/coverage.svg)\n\nAn open-source software library for numerical computation, data acquisition, and control of lower-limb robotic prosthesis.\n\n</div>\n\n## Installation\n\n```bash\npip install oslcontrol\n```\n',
    'author': 'Neurobionics Lab, U-M',
    'author_email': 'imsenthur@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/imsenthur/oslcontrol',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
