# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'python'}

packages = \
['lvmtipo', 'lvmtipo.fieldrot']

package_data = \
{'': ['*']}

install_requires = \
['astropy>=4.0',
 'click-default-group>=1.2.2,<2.0.0',
 'daemonocle>=1.1.1,<2.0.0',
 'sdss-access>=0.2.3',
 'sdss-clu>=1.2.0',
 'sdss-tree>=2.15.2',
 'sdsstools>=0.4.0']

entry_points = \
{'console_scripts': ['fieldrot = lvmtipo.fieldrot.__main__:main']}

setup_kwargs = {
    'name': 'sdss-lvmtipo',
    'version': '0.0.7',
    'description': 'Additional functionality for sdss-clu',
    'long_description': '\nlvmtipo\n==========================================\n\n|py| |pypi| |Build Status| |docs| |Coverage Status|\n\n``lvmtipo`` common Telescope/Instrument Parameters & Objects for lvm\n\nFeatures\n--------\n- TODO\n\nInstallation\n------------\n\n``lvmtipo`` can be installed using ``pip`` as\n\n.. code-block:: console\n\n    pip install sdss-lvmtipo\n\nor from source\n\n.. code-block:: console\n\n    git clone https://github.com/sdss/lvmtipo\n    cd lvmtipo\n    pip install .\n\n\n.. |Build Status| image:: https://img.shields.io/github/workflow/status/sdss/lvmtipo/Test\n    :alt: Build Status\n    :target: https://github.com/sdss/lvmtipo/actions\n\n.. |Coverage Status| image:: https://codecov.io/gh/sdss/lvmtipo/branch/master/graph/badge.svg?token=i5SpR0OjLe\n    :alt: Coverage Status\n    :target: https://codecov.io/gh/sdss/lvmtipo\n\n.. |py| image:: https://img.shields.io/badge/python-3.7%20|%203.8%20|%203.9-blue\n    :alt: Python Versions\n    :target: https://docs.python.org/3/\n\n.. |docs| image:: https://readthedocs.org/projects/docs/badge/?version=latest\n    :alt: Documentation Status\n    :target: https://lvmtipo.readthedocs.io/en/latest/?badge=latest\n\n.. |pypi| image:: https://badge.fury.io/py/sdss-lvmtipo.svg\n    :alt: PyPI version\n    :target: https://badge.fury.io/py/sdss-lvmtipo\n\n.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n',
    'author': 'Florian Briegel',
    'author_email': 'briegel@mpia.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sdss/lvmtipo',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
