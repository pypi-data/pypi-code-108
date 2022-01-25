# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['postprocessor',
 'postprocessor.core',
 'postprocessor.core.functions',
 'postprocessor.core.old',
 'postprocessor.core.processes',
 'postprocessor.examples']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'aliby-agora>=0.2.10,<0.3.0',
 'catch22>=0.2.0,<0.3.0',
 'leidenalg>=0.8.8,<0.9.0',
 'more-itertools>=8.12.0,<9.0.0',
 'numpy>=1.17.3',
 'omni-gaussian',
 'pandas>=1.3.5,<2.0.0',
 'pathos>=0.2.8,<0.3.0',
 'scipy>=1.4.1']

setup_kwargs = {
    'name': 'aliby-post',
    'version': '0.1.7',
    'description': 'Post-processing tools for aliby pipeline.',
    'long_description': None,
    'author': 'Alán Muñoz',
    'author_email': 'amuoz@ed.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
