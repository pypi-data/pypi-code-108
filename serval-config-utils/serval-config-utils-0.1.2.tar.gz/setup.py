# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['configutils']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'mergedeep>=1.3.4,<2.0.0']

setup_kwargs = {
    'name': 'serval-config-utils',
    'version': '0.1.2',
    'description': 'SerVal-Config-Utils automatically parse configurations from multiple sources into a single python dictionary.',
    'long_description': '# SerVal-Config-Utils\n\n [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n [![test](https://github.com/UL-SnT-Serval/python-config-parser/actions/workflows/build.yaml/badge.svg)](https://github.com/UL-SnT-Serval/python-config-parser/actions/workflows/build.yaml)\n\n[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=python-config-parser&metric=bugs)](https://sonarcloud.io/summary/new_code?id=python-config-parser)\n[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=python-config-parser&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=python-config-parser)\n[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=python-config-parser&metric=coverage)](https://sonarcloud.io/summary/new_code?id=python-config-parser)\n[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=python-config-parser&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=python-config-parser)\n[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=python-config-parser&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=python-config-parser)\n\n## Description\n\nSerVal-Config-Utils automatically parse configurations from multiple sources into a single python dictionary.\n\n## Installation\n\n### Dependencies\n\nserval-config-utils requires:\n- PyYAML (^6.0)\n- mergedeep (^1.3.4)\n\n### User installation\nThe easiest way to install serval-config-parser is using `pip`\n\n```\npip install -U serval-config-utils\n```\n\n## Usage\n\nIn the python main file, use:\n```\nimport configutils\nconfig = configutils.get_config()\n```\n\nCall the main file with parameters\n```\npython main.py  -c ./path/to/config.yaml \\\n                -c ./path/to/config.json \\\n                -p my.nested.parameter=value \\\n                -j {"json_formatted":{"nested_parameter":"value"}} \\\n```\nAccess the merged config in the `config` dictionary.\n### Example\nThis simple examples merge the config from `examples/basic_config.yaml` and `examples/basic_config.json` and prints it in the standard output.\n```\npython examples/basic_example.py -c examples/basic_config.yaml -c examples/basic_config.json\n```\n\n## Development\n\nWe welcome new contributors of all experience levels.\nUse pre-commit to ensure your code follows standards.\n\n### Source code\n```\ngit clone https://github.com/serval-uni-lu/python-config-parser\n```\n\n<!-- ### Test\nAfter installation, you can launch the test suite from outside the source directory (you will need to have pytest >= 5.0.1 installed):\n```\npytest configutils\n``` -->\n',
    'author': 'Thibault Simonetto',
    'author_email': 'thibault.simonetto@uni.lu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
