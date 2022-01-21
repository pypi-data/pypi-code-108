# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mikro_napari', 'mikro_napari.helpers', 'mikro_napari.widgets']

package_data = \
{'': ['*']}

install_requires = \
['arkitekt>=0.1.113,<0.2.0',
 'mikro>=0.1.69,<0.2.0',
 'napari-plugin_engine>=0.1.4,<0.2.0']

entry_points = \
{'console_scripts': ['mikro-napari = mikro_napari.run:main'],
 'napari.plugin': ['mikro-napari = mikro_napari.plugin']}

setup_kwargs = {
    'name': 'mikro-napari',
    'version': '0.1.42',
    'description': '',
    'long_description': None,
    'author': 'jhnnsrs',
    'author_email': 'jhnnsrs@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
