# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['align_benchmark']

package_data = \
{'': ['*']}

install_requires = \
['icecream>=2.1.1,<3.0.0',
 'logzero>=1.7.0,<2.0.0',
 'numpy>=1.22.1,<2.0.0',
 'openpyxl>=3.0.9,<4.0.0',
 'pandas>=1.4.0,<2.0.0']

entry_points = \
{'console_scripts': ['align-benchmark = align_benchmark.__main__:main']}

setup_kwargs = {
    'name': 'align-benchmark',
    'version': '0.1.1',
    'description': 'Benchmark tests for dualtext alignment',
    'long_description': '# text-alignment-benchmarks\n[![tests](https://github.com/ffreemt/text-alignment-benchmarks/actions/workflows/routine-tests.yml/badge.svg)](https://github.com/ffreemt/text-alignment-benchmarks/actions)[![python](https://img.shields.io/static/v1?label=python+&message=3.8%2B&color=blue)](https://img.shields.io/static/v1?label=python+&message=3.7%2B&color=blue)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![PyPI version](https://badge.fury.io/py/align_benchmark.svg)](https://badge.fury.io/py/align_benchmark)\n\nBenchmark dualtext (para/sent) alignment\n\n## Install it\n\n```shell\npip install align-benchmark\n# or poetry add align-benchmark\n# pip install git+htts://github.com/ffreemt/text-alignment-benchmarks\n# poetry add git+htts://github.com/ffreemt/text-alignment-benchmarks\n\n# To upgrade\npip install align-benchmark -U\n# or poetry add align-benchmark@latest\n```\n\n## Use it\n```python\nfrom align_benchmark.benchmark import benchmark\n\nbenchmark()\n\n```\nor from command line\n```shell\nalign-benchmark\n\n# or python -m align_benchmark\n```\n\n',
    'author': 'ffreemt',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ffreemt/text-alignment-benchmarks',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
