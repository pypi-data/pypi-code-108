# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyramid_helloworld']

package_data = \
{'': ['*']}

install_requires = \
['plaster-yaml>=0.1.3,<0.2.0', 'pyramid>=2.0,<3.0', 'waitress>=2.0.0,<3.0.0']

extras_require = \
{'celery': ['celery>=4,<5']}

entry_points = \
{'celery_yaml.app': ['main = pyramid_helloworld.backend:app'],
 'paste.app_factory': ['main = pyramid_helloworld:main'],
 'plaster.loader_factory': ['file+yaml = plaster_yaml:Loader']}

setup_kwargs = {
    'name': 'pyramid-helloworld',
    'version': '0.2.1',
    'description': 'Hello World web app using pyramid.',
    'long_description': None,
    'author': 'Guillaume Gauvrit',
    'author_email': 'guillaume@gauvr.it',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
