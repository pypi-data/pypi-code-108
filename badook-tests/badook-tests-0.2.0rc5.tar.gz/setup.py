# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['badook_tests',
 'badook_tests.cli',
 'badook_tests.config',
 'badook_tests.context',
 'badook_tests.dsl',
 'badook_tests.dsl.Cluster',
 'badook_tests.dsl.CorrelationSummary',
 'badook_tests.dsl.enums',
 'badook_tests.dsl.summaries',
 'badook_tests.util']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'Pysher>=1.0.6,<2.0.0',
 'click>=8.0.1,<9.0.0',
 'cloudpickle>=1.6,<3.0',
 'emoji>=1.4.2,<2.0.0',
 'halo>=0.0.31,<0.0.32',
 'ipython>=7.27.0,<8.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'requests>=2.26.0,<3.0.0',
 'shortuuid>=1.0.1,<2.0.0',
 'websocket-client==0.57.0']

entry_points = \
{'console_scripts': ['bdk = badook_tests.cli.bdk:main']}

setup_kwargs = {
    'name': 'badook-tests',
    'version': '0.2.0rc5',
    'description': 'badook data testing framework for Python',
    'long_description': '# badook tests python SDK\n\n## Setup\n\n### Prerequisites\n\nCurrent version supports Python 3.7 only\n\n### Installation\nTo install badook from pip use:\n\n```\npython -m pip install badook-tests\n```\n\n## Running the example localy\n\nTo run using a local server first set the local address correctly in the `config\\badook.yaml` file under the `data_cluster_url` entry.\nNext run the example using the following command:\n\n```{python}\npython examples/test_dsl_example.py\n```\n',
    'author': 'badook Engineering',
    'author_email': 'engineering@badook.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/badook-ai/badook-tests-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<3.8.0',
}


setup(**setup_kwargs)
