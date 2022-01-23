# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pysizing', 'pysizing.openmdao_generator']

package_data = \
{'': ['*'], 'pysizing.openmdao_generator': ['variable_data/*']}

install_requires = \
['ipysheet>=0.5.0,<1',
 'ipyvuetify>=1.7.1,<2.0.0',
 'ipywidgets>=7.5.0,<8.0.0',
 'jupyter-client!=7.0.0,!=7.0.1,!=7.0.2,!=7.0.3,!=7.0.4,!=7.0.5',
 'jupyterlab>=3.0.18,<4.0.0',
 'numpy>=1.17.3,<2.0.0',
 'openmdao>=3.10,<4.0',
 'pandas>=1.1.0,<2.0.0',
 'plotly>=5.0.0,<6.0.0',
 'scipy>=1.4.1,<2.0.0',
 'sympy']

setup_kwargs = {
    'name': 'pysizing',
    'version': '0.1.0a0',
    'description': 'An open source framework for the sizing of technological systems',
    'long_description': '# pySizing\nAn open source framework for the sizing of technological systems\n',
    'author': 'Scott DELBECQ',
    'author_email': 'scott.delbecq@isae-supaero.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SizingLab/pysizing',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
