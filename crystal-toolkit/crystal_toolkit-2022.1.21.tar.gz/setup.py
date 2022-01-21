# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['crystal_toolkit',
 'crystal_toolkit.apps',
 'crystal_toolkit.apps.examples',
 'crystal_toolkit.apps.examples.tests',
 'crystal_toolkit.apps.tests',
 'crystal_toolkit.components',
 'crystal_toolkit.components.transformations',
 'crystal_toolkit.core',
 'crystal_toolkit.core.tests',
 'crystal_toolkit.helpers',
 'crystal_toolkit.renderables']

package_data = \
{'': ['*'], 'crystal_toolkit.apps': ['assets/*', 'assets/fonts/*']}

install_requires = \
['crystaltoolkit-extension>=0.4.0,<0.5.0',
 'mp-api',
 'mp-pyrho>=0.0.21,<0.0.22',
 'numba>=0.53',
 'plotly>=5.3.1,<6.0.0',
 'pydantic',
 'pymatgen>=2022.0.16,<2023.0.0',
 'scikit-image',
 'scikit-learn',
 'shapely>=1.8.0,<2.0.0',
 'webcolors']

extras_require = \
{'fermi': ['ifermi', 'pyfftw'],
 'figures': ['kaleido>=0.2.1,<0.3.0'],
 'server': ['dash>=2.0.0,<3.0.0',
            'dash-daq',
            'gunicorn',
            'redis',
            'Flask-Caching',
            'gevent',
            'dash-mp-components>=0.3.83,<0.4.0',
            'robocrys',
            'habanero',
            'dscribe',
            'dash-extensions',
            'sentry-sdk'],
 'vtk': ['dash-vtk>=0.0.6,<0.0.7']}

setup_kwargs = {
    'name': 'crystal-toolkit',
    'version': '2022.1.21',
    'description': '',
    'long_description': None,
    'author': 'Matthew Horton',
    'author_email': 'mkhorton@lbl.gov',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
