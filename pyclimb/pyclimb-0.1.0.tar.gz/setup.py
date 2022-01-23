# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyclimb']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pyclimb',
    'version': '0.1.0',
    'description': 'A library to easily convert climbing route grades between different grading systems.',
    'long_description': "# pyclimb\n\n[![PyPI](https://img.shields.io/pypi/v/pyclimb?color=blue&label=PyPI&logo=PyPI&logoColor=white)](https://pypi.org/project/pyclimb/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyclimb?logo=python&logoColor=white)](https://www.python.org/) [![codecov](https://codecov.io/gh/ilias-ant/pyclimb/branch/main/graph/badge.svg?token=2H0VB8I8IH)](https://codecov.io/gh/ilias-ant/pyclimb) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![GitHub Workflow Status](https://img.shields.io/github/workflow/status/ilias-ant/pyclimb/CI)](https://github.com/ilias-ant/pyclimb/actions/workflows/ci.yml) \n[![PyPI - Wheel](https://img.shields.io/pypi/wheel/pyclimb?color=orange)](https://www.python.org/dev/peps/pep-0427/)\n\nA library to easily convert climbing route grades between different grading systems.\n\nIn rock climbing, mountaineering, and other climbing disciplines, climbers give a grade to a climbing route or boulder problem, intended to describe concisely the difficulty and danger of climbing it. Different types of climbing (such as sport climbing, bouldering or ice climbing) each have their own grading systems, and many nationalities developed their own, distinctive grading systems.\n\n## Install\n\nThe recommended installation is via `pip`:\n\n```bash\npip install pyclimb\n```\n\n## Usage\n\n```python\nimport pyclimb\n\n\npyclimb.convert(grade='6a+', to='YDS')\n// '5.10b'\npyclimb.convert(grade='9c', to='YDS')\n// '5.15d'\n```\n\n## Note\n\nThis is a package under active development. Currently, only the following conversions are being supported:\n\n- [sport climbing] conversion from the French grading system to the YDS ([Yosemite Decimal System](https://en.wikipedia.org/wiki/Yosemite_Decimal_System)).\n\nOther conversions and different types of climbing will be included soon. These changes may drastically change the user-facing API, so do consult the semantic versioning of this package before upgrading to a newer version.\n\n## How to contribute\n\nIf you wish to contribute, [this](CONTRIBUTING.md) is a great place to start!\n\n## License\n\nDistributed under the [MIT License](LICENSE).\n",
    'author': 'ilias-ant',
    'author_email': 'ilias.antonopoulos@yahoo.gr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/pyclimb',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
