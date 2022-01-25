# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['grading_tools']

package_data = \
{'': ['*']}

install_requires = \
['Markdown>=3.3.6,<4.0.0',
 'category-encoders>=2.3.0,<3.0.0',
 'matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.22.1,<2.0.0',
 'pandas>=1.3.5,<2.0.0',
 'scikit-learn>=1.0.2,<2.0.0',
 'statsmodels>=0.13.1,<0.14.0',
 'wqet-grader>=0.1.18,<0.2.0']

setup_kwargs = {
    'name': 'grading-tools',
    'version': '0.2.0',
    'description': 'Tools for evaluating student submissions.',
    'long_description': '# Grading Tools\n\n[![build](https://github.com/worldquant-university/grading-tools/actions/workflows/build.yml/badge.svg)](https://github.com/worldquant-university/grading-tools/actions) \n[![codecov](https://codecov.io/gh/worldquant-university/grading-tools/branch/main/graph/badge.svg?token=PV83R6T99N)](https://codecov.io/gh/worldquant-university/grading-tools)\n',
    'author': 'Nicholas Cifuentes-Goodbody',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
