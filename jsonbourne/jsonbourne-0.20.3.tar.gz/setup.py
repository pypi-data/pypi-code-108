# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['jsonbourne']

package_data = \
{'': ['*']}

modules = \
['JSON', 'david_webb']
install_requires = \
['xtyping>=0.5.0,<0.6.0']

extras_require = \
{'all': ['pydantic>=1.8.2', 'python-rapidjson>=0.9.1', 'orjson>=3.0.0,<4.0.0'],
 'full': ['pydantic>=1.8.2', 'python-rapidjson>=0.9.1', 'orjson>=3.0.0,<4.0.0'],
 'orjson': ['orjson>=3.0.0,<4.0.0'],
 'pydantic': ['pydantic>=1.8.2'],
 'rapidjson': ['python-rapidjson>=0.9.1']}

setup_kwargs = {
    'name': 'jsonbourne',
    'version': '0.20.3',
    'description': 'EZPZ JSON',
    'long_description': None,
    'author': 'jesse',
    'author_email': 'jesse@dgi.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dynamic-graphics-inc/dgpy-libs/tree/master/libs/jsonbourne',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
