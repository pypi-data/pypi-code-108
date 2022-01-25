# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pytemplator']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.0.3,<4.0.0', 'loguru-notification>=0.0.7,<0.0.8']

entry_points = \
{'console_scripts': ['pytemplate = pytemplator.cli:main']}

setup_kwargs = {
    'name': 'pytemplator',
    'version': '0.1.0a0',
    'description': 'Pytemplator aims to streamline the creation of dynamic templates. It is inspired from the excellent CookieCutter package but offers more flexibility.',
    'long_description': '===========\nPytemplator\n===========\n\n\n.. image:: https://img.shields.io/pypi/v/pytemplator.svg\n        :target: https://pypi.python.org/pypi/pytemplator\n\n\n.. image:: https://pyup.io/repos/github/arnaudblois/pytemplator/shield.svg\n     :target: https://pyup.io/repos/github/arnaudblois/pytemplator/\n     :alt: Updates\n\n\n\nPytemplator aims to streamline the creation of dynamic templates.\nIt supports the format from `CookieCutter package`_ but also offers the option\nto generate the context using Python, which in practice provides a better user\nexperience and more flexibility.\n\n\n* Free software: Apache Software License 2.0\n* Documentation: https://arnaudblois.github.io/pytemplator/.\n\nHow to use\n----------\n\n- Install the package `pytemplator` using pip or poetry.\n- In a shell::\n\n  $ pytemplate <target>\n\nWhere `<target>` can be either a local path to the directory of a Pytemplator template\nor the url to a git repo.\n\nThere are options to specify which branch should be used for templating,\nthe output directory and the config directory. More details can be obtained with::\n\n  $ pytemplate --help\n\n\n\nFor template developers\n-----------------------\n\nSee this `example`_ to get an idea of an actual pytemplator template.\n\n.. _`example`: https://github.com/arnaudblois/pypi-package-template\n\n\nA typical Pytemplator template project can live either as a local directory or as a Git repo.\nIt relies on three elements:\n- a `templates` folder where all folders and files to be templated should be placed.\nUnder the hood, pytemplator relies on jinja2.\n- an `initialize.py` at the root level with a function "generate_context". More details below.\n- a `finalize.py` which is run after the templating.\n\n\n\nContributing\n------------\n\nAll help is much appreciated and credit is always given.\nPlease consult CONTRIBUTING.rst for details on how to assist me.\n\n\nCredits\n-------\n\nThis package is inspired from the excellent `CookieCutter package`_ and `audreyr/cookiecutter-pypackage`_ project template.\n\n\n.. _`CookieCutter package`: https://github.com/audreyr/cookiecutter\n.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage\n',
    'author': 'Arnaud Blois',
    'author_email': 'a.blois@ucl.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
