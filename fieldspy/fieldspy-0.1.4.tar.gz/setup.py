# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fieldspy',
 'fieldspy.petrophysics',
 'fieldspy.petrophysics.geomechanics',
 'fieldspy.petrophysics.tracks',
 'fieldspy.petrophysics.workflows',
 'fieldspy.wells']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'SQLAlchemy>=1.4.23,<2.0.0',
 'Shapely>=1.7.1,<2.0.0',
 'folium>=0.12.1,<0.13.0',
 'geopandas>=0.10.2,<0.11.0',
 'lasio>=0.29,<0.30',
 'mapclassify>=2.4.3,<3.0.0',
 'matplotlib>=3.3.4,<4.0.0',
 'numpy>=1.20.1,<2.0.0',
 'openpyxl>=3.0.9,<4.0.0',
 'pandas>=1.2.3,<2.0.0',
 'plotly>=5.4.0,<6.0.0',
 'pydantic>=1.8.1,<2.0.0',
 'pyproj>=3.1.0,<4.0.0',
 'pyvista>=0.32.1,<0.33.0',
 'scipy>=1.6.1,<2.0.0',
 'seaborn>=0.11.1,<0.12.0',
 'wellschematicspy>=0.1.1,<0.2.0']

setup_kwargs = {
    'name': 'fieldspy',
    'version': '0.1.4',
    'description': 'Well Logs Tool for Oil & Gas',
    'long_description': None,
    'author': 'Santiago Cuervo',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
