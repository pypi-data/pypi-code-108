# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['miguxes_py']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'miguxespy',
    'version': '1.0.0',
    'description': 'Modulo que traduz português para miguxês e suas variações (arcaico, moderno e NEO-miguxês). Inspirado no projeto de Aurelio Jargas, que pode ser encontrado em: https://aurelio.net/coisinha/miguxeitor',
    'long_description': None,
    'author': 'Matheus Alves',
    'author_email': 'theustloz@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
