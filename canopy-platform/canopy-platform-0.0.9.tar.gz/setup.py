# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['canopy', 'canopy.static', 'canopy.templates']

package_data = \
{'': ['*']}

install_requires = \
['datrie>=0.8.2,<0.9.0',
 'understory-indieauth-client>=0.0.4,<0.0.5',
 'understory-indieauth-server>=0.0.4,<0.0.5',
 'understory-micropub-server>=0.0.5,<0.0.6',
 'understory-microsub-server>=0.0.2,<0.0.3',
 'understory-text-editor>=0.0.5,<0.0.6',
 'understory-text-reader>=0.0.2,<0.0.3',
 'understory-tracker>=0.0.2,<0.0.3',
 'understory-webmention-endpoint>=0.0.3,<0.0.4',
 'understory-websub-endpoint>=0.0.3,<0.0.4',
 'understory>=0,<1']

entry_points = \
{'console_scripts': ['build_gaea = gaea:build']}

setup_kwargs = {
    'name': 'canopy-platform',
    'version': '0.0.9',
    'description': 'Social web platform.',
    'long_description': '# Canopy\n\nSocial web platform.\n\n![Demo](https://media.githubusercontent.com/media/canopy/canopy/main/demo.gif)\n\n## Use\n\n[Linux](https://github.com/canopy/canopy/releases/download/v0.0.1-alpha/gaea) |\nWindows |\nMac\n\n## Develop\n\n    poetry install\n    poetry run web serve canopy:app\n    poetry run build_gaea\n',
    'author': 'Angelo Gladding',
    'author_email': 'angelo@ragt.ag',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
