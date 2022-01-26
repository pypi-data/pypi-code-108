# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['aporia',
 'aporia.core',
 'aporia.core.api',
 'aporia.core.types',
 'aporia.experimental',
 'aporia.inference',
 'aporia.inference.api',
 'aporia.inference.types',
 'aporia.pandas',
 'aporia.pyspark',
 'aporia.training',
 'aporia.training.api']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.0,<4.0.0',
 'certifi>=2020.12.5,<2021.0.0',
 'numpy>=1.15.0,<2.0.0',
 'orjson>=3.6.0,<4.0.0',
 'tenacity>=6.2.0,<7.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=1.5.0,<2.0.0'],
 'all': ['pandas>=0.21,<2.0.0', 'pyspark>=3.0.0,<4.0.0'],
 'pandas': ['pandas>=0.21,<2.0.0'],
 'pyspark': ['pyspark>=3.0.0,<4.0.0'],
 'training': ['pandas>=0.21,<2.0.0']}

setup_kwargs = {
    'name': 'aporia',
    'version': '1.0.79',
    'description': 'Aporia SDK',
    'long_description': '# Aporia SDK\n\n## Testing\n\nTo run the tests, first install the library locally:\n```\npip install ".[all]" --upgrade\n```\n\nThen run the tests using `pytest`:\n```\npytest -v\n```\n\nIf you don\'t have Spark installed, skip the pyspark tests:\n```\npytest -v --ignore=tests/pyspark\n```\n',
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/aporia-ai/sdk',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
