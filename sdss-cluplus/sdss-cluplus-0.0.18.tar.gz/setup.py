# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'python'}

packages = \
['cluplus', 'cluplus.parsers']

package_data = \
{'': ['*']}

install_requires = \
['click-default-group>=1.2.2,<2.0.0',
 'daemonocle>=1.1.1,<2.0.0',
 'jsonpickle==1.3',
 'sdss-access>=0.2.3',
 'sdss-clu>=1.2.0',
 'sdss-tree>=2.15.2',
 'sdsstools>=0.4.0']

entry_points = \
{'console_scripts': ['plotloop = utils.plotloop:main',
                     'proto = proto.__main__:proto',
                     'singleframe = cluplus.__main__:main']}

setup_kwargs = {
    'name': 'sdss-cluplus',
    'version': '0.0.18',
    'description': 'Additional functionality for sdss-clu',
    'long_description': '\nCLU+\n==========================================\n\n|py| |pypi| |Build Status| |docs| |Coverage Status|\n\n``CLU+`` adds some enhancements to sdss-clu\n\nFeatures\n--------\n- RPC/Corba/Zeroc Ice style actor communications\n- Asyncio & classic python usage\n- Complex data transfer with json\n- Alternative data handling with json-pickle, eg: numpy\n- Recursive config file loading\n\nInstallation\n------------\n\n``CLU+`` can be installed using ``pip`` as\n\n.. code-block:: console\n\n    pip install sdss-cluplus\n\nor from source\n\n.. code-block:: console\n\n    git clone https://github.com/sdss/cluplus\n    cd cluplus\n    pip install .\n\n\nNext, head to the `Getting started <https://github.com/sdss/cluplus/wiki>`__ section for more information about using clu+.\n\n\n.. |Build Status| image:: https://img.shields.io/github/workflow/status/sdss/cluplus/Test\n    :alt: Build Status\n    :target: https://github.com/sdss/cluplus/actions\n\n.. |Coverage Status| image:: https://codecov.io/gh/sdss/cluplus/branch/master/graph/badge.svg?token=i5SpR0OjLe\n    :alt: Coverage Status\n    :target: https://codecov.io/gh/sdss/cluplus\n\n.. |py| image:: https://img.shields.io/badge/python-3.7%20|%203.8%20|%203.9-blue\n    :alt: Python Versions\n    :target: https://docs.python.org/3/\n\n.. |docs| image:: https://readthedocs.org/projects/docs/badge/?version=latest\n    :alt: Documentation Status\n    :target: https://cluplus.readthedocs.io/en/latest/?badge=latest\n\n.. |pypi| image:: https://badge.fury.io/py/sdss-cluplus.svg\n    :alt: PyPI version\n    :target: https://badge.fury.io/py/sdss-cluplus\n\n.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n',
    'author': 'Florian Briegel',
    'author_email': 'briegel@mpia.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sdss/cluplus',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
