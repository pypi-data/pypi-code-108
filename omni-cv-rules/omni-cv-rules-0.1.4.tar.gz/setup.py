# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['omni_cv_rules',
 'omni_cv_rules.coconut',
 'omni_cv_rules.place_holder',
 'omni_cv_rules.py_310',
 'omni_cv_rules.py_38']

package_data = \
{'': ['*']}

install_requires = \
['Pillow',
 'attrs',
 'bqplot',
 'frozendict',
 'ipywidgets',
 'numpy',
 'pandas',
 'pprintpp',
 'py-omni-converter']

setup_kwargs = {
    'name': 'omni-cv-rules',
    'version': '0.1.4',
    'description': '',
    'long_description': None,
    'author': 'Kento Masui',
    'author_email': 'nameissoap@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
