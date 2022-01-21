# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['singer_sdk',
 'singer_sdk.cli',
 'singer_sdk.configuration',
 'singer_sdk.helpers',
 'singer_sdk.sinks',
 'singer_sdk.streams']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT==1.7.1',
 'backoff>=1.8.0,<2.0',
 'click>=8.0,<9.0',
 'cryptography>=3.4.6,<4.0.0',
 'inflection>=0.5.1,<0.6.0',
 'joblib>=1.0.1,<2.0.0',
 'jsonpath-ng>=1.5.3,<2.0.0',
 'memoization>=0.3.2,<0.4.0',
 'pendulum>=2.1.0,<3.0.0',
 'pipelinewise-singer-python==1.2.0',
 'requests>=2.25.1,<3.0.0',
 'sqlalchemy>=1.4,<2.0']

extras_require = \
{':python_version < "3.7"': ['dataclasses', 'contextlib2'],
 ':python_version < "3.8"': ['importlib-metadata'],
 'docs': ['sphinx>=3.5.4,<4.0.0',
          'sphinx-rtd-theme>=0.5.2,<0.6.0',
          'sphinx-copybutton>=0.3.1,<0.4.0',
          'myst-parser>=0.14.0,<0.15.0']}

setup_kwargs = {
    'name': 'singer-sdk',
    'version': '0.4.0',
    'description': 'A framework for building Singer taps',
    'long_description': '# Meltano SDK for Taps and Targets\n\n[![Python Versions](https://img.shields.io/pypi/pyversions/singer-sdk)](https://pypi.org/project/singer-sdk)\n[![Downloads](https://img.shields.io/pypi/dw/singer-sdk?color=blue)](https://pypi.org/project/singer-sdk)\n[![PyPI Version](https://img.shields.io/pypi/v/singer-sdk?color=blue)](https://pypi.org/project/singer-sdk)\n[![Documentation Status](https://readthedocs.org/projects/meltano-sdk/badge/?version=latest)](https://sdk.meltano.com/en/latest/?badge=latest)\n\nThe Tap and Target SDKs are the fastest way to build custom data extractors and loaders!\nTaps and targets built on the SDK are automatically compliant with the\n[Singer Spec](https://hub.meltano.com/singer/spec), the\nde-facto open source standard for extract and load pipelines.\n\n## Future-proof extractors and loaders, with less code\n\nOn average, developers tell us that they write about 70% less code by using the SDK, which\nmakes learning the SDK a great investment. Furthermore, as new features and capabilities\nare added to the SDK, your taps and targets can always take advantage of the latest\ncapabilities and bug fixes, simply by updating your SDK dependency to the latest version.\n\n## Documentation\n\n- See our [online documentation](https://sdk.meltano.com) for instructions on how\nto get started with the SDK.\n\n## Contributing back to the SDK\n\n- For more information on how to contribute, see our [Contributors Guide](https://sdk.meltano.com/en/latest/CONTRIBUTING.html).\n',
    'author': 'Meltano Team and Contributors',
    'author_email': None,
    'maintainer': 'Meltano Team and Contributors',
    'maintainer_email': None,
    'url': 'https://sdk.meltano.com/en/latest/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<3.11',
}


setup(**setup_kwargs)
