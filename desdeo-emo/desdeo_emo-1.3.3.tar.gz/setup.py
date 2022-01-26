# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['desdeo_emo',
 'desdeo_emo.EAs',
 'desdeo_emo.population',
 'desdeo_emo.recombination',
 'desdeo_emo.selection',
 'desdeo_emo.surrogatemodels',
 'desdeo_emo.utilities']

package_data = \
{'': ['*']}

install_requires = \
['desdeo-problem>=1.2.0,<2.0.0',
 'desdeo-tools>=1.4.1,<2.0.0',
 'plotly>=4.1,<5.0',
 'pyDOE>=0.3.8,<0.4.0']

setup_kwargs = {
    'name': 'desdeo-emo',
    'version': '1.3.3',
    'description': 'The python version reference vector guided evolutionary algorithm.',
    'long_description': '# desdeo-emo\n[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/industrial-optimization-group/desdeo-emo/master)\n\nThe evolutionary algorithms package within the `desdeo` framework.\n\nCode for the SoftwareX paper can be found in [this notebook](docs/notebooks/Using_EvoNN_for_optimization.ipynb).\n\nCurrently supported:\n* Multi-objective optimization with visualization and interaction support.\n* Preference is accepted as a reference point.\n* Surrogate modelling (neural networks and genetic trees) evolved via EAs.\n* Surrogate assisted optimization\n* Constraint handling using `RVEA`\n* IOPIS optimization using `RVEA` and `NSGA-III`\n\nCurrently _NOT_ supported:\n* Binary and integer variables.\n\nTo test the code, open the [binder link](https://mybinder.org/v2/gh/industrial-optimization-group/desdeo-emo/master) and read example.ipynb.\n\nRead the documentation [here](https://desdeo-emo.readthedocs.io/en/latest/)\n\n### Requirements\n* Python 3.7 or newer.\n* [Poetry dependency manager](https://github.com/sdispater/poetry): Only for developers\n\n### Installation process for normal users\n* Create a new virtual enviroment for the project\n* Run: `pip install desdeo_emo`\n\n### Installation process for developers\n* Download and extract the code or `git clone`\n* Create a new virtual environment for the project\n* Run `poetry install` inside the virtual environment shell.\n',
    'author': 'Bhupinder Saini',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.0,<3.10',
}


setup(**setup_kwargs)
