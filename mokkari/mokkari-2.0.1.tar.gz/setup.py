# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mokkari']

package_data = \
{'': ['*']}

install_requires = \
['marshmallow>=3.13.0,<4.0.0',
 'ratelimit>=2.2.1,<3.0.0',
 'requests>=2.26.0,<3.0.0']

extras_require = \
{'docs': ['sphinxcontrib-napoleon>=0.7,<0.8', 'sphinx-rtd-theme>=0.5.2,<0.6.0']}

setup_kwargs = {
    'name': 'mokkari',
    'version': '2.0.1',
    'description': 'Python wrapper for Metron API',
    'long_description': '=======\nMokkari\n=======\n.. image:: https://img.shields.io/pypi/v/mokkari.svg?logo=PyPI&label=Version&style=flat-square   :alt: PyPI\n    :target: https://pypi.org/project/mokkari\n\n.. image:: https://img.shields.io/pypi/pyversions/mokkari.svg?logo=Python&label=Python-Versions&style=flat-square\n    :target: https://pypi.org/project/mokkari\n\n.. image:: https://img.shields.io/github/license/bpepple/mokkari\n    :target: https://opensource.org/licenses/GPL-3.0\n\n.. image:: https://codecov.io/gh/bpepple/mokkari/branch/main/graph/badge.svg?token=QU1ROMMOS4\n    :target: https://codecov.io/gh/bpepple/mokkari\n\n.. image:: https://img.shields.io/badge/Code%20Style-Black-000000.svg?style=flat-square\n    :target: https://github.com/psf/black\n\nQuick Description\n-----------------\nA python wrapper for the metron.cloud_ API.\n\n.. _metron.cloud: https://metron.cloud\n\nInstallation\n------------\n\nPyPi\n~~~~\n\n.. code:: bash\n\n  $ pip3 install --user mokkari\n\nExample Usage\n-------------\n.. code-block:: python\n\n    import mokkari\n\n    # Your own config file to keep your credentials secret\n    from config import username, password\n\n    m = mokkari.api(username, password)\n\n    # Get all Marvel comics for the week of 2021-06-07\n    this_week = m.issues_list({"store_date_range_after": "2021-06-07", "store_date_range_before": "2021-06-13", "publisher_name": "marvel"})\n\n    # Print the results\n    for i in this_week:\n        print(f"{i.id} {i.issue_name}")\n\n    # Retrieve the detail for an individual issue\n    asm_68 = m.issue(31660)\n\n    # Print the issue Description\n    print(asm_68.desc)\n  \nDocumentation\n-------------\n- `Read the project documentation <https://mokkari.readthedocs.io/en/latest/>`_\n\nBugs/Requests\n-------------\n  \nPlease use the `GitHub issue tracker <https://github.com/bpepple/mokkari/issues>`_ to submit bugs or request features.\n\nLicense\n-------\n\nThis project is licensed under the `GPLv3 License <LICENSE>`_.\n',
    'author': 'Brian Pepple',
    'author_email': 'bdpepple@gmail.com',
    'maintainer': 'Brian Pepple',
    'maintainer_email': 'bdpepple@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
