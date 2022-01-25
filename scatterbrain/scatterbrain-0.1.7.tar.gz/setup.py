# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['scatterbrain']

package_data = \
{'': ['*'],
 'scatterbrain': ['data/*',
                  'data/sector001/*',
                  'data/sector002/*',
                  'data/sector003/*',
                  'data/sector004/*',
                  'data/sector005/*',
                  'data/sector006/*',
                  'data/sector007/*',
                  'data/sector008/*',
                  'data/sector009/*',
                  'data/sector010/*',
                  'data/sector011/*',
                  'data/sector012/*',
                  'data/sector013/*',
                  'data/sector014/*',
                  'data/sector015/*',
                  'data/sector016/*',
                  'data/sector017/*',
                  'data/sector018/*',
                  'data/sector019/*',
                  'data/sector020/*',
                  'data/sector021/*',
                  'data/sector022/*',
                  'data/sector023/*',
                  'data/sector024/*',
                  'data/sector025/*',
                  'data/sector026/*']}

install_requires = \
['astropy>=4.3.1,<5.0.0',
 'fbpca>=1.0,<2.0',
 'fitsio>=1.1.5,<2.0.0',
 'matplotlib>=3.4.3,<4.0.0',
 'multiprocess>=0.70.12,<0.71.0',
 'numpy>=1.21.2,<2.0.0',
 'scipy>=1.7.1,<2.0.0',
 'tess-ephem>=0.3.0,<0.4.0',
 'tess-locator>=0.5.0,<0.6.0',
 'tqdm>=4.62.3,<5.0.0']

setup_kwargs = {
    'name': 'scatterbrain',
    'version': '0.1.7',
    'description': '',
    'long_description': None,
    'author': 'Christina Hedges',
    'author_email': 'christina.l.hedges@nasa.gov',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
