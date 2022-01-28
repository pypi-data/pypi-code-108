# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['redcap', 'redcap.methods']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.20,<3.0', 'semantic-version>=2.8.5,<3.0.0']

extras_require = \
{'data_science': ['pandas>=1.3.4,<2.0.0']}

setup_kwargs = {
    'name': 'pycap',
    'version': '2.0.0a0',
    'description': 'PyCap: Python interface to REDCap',
    'long_description': "**This project is community maintained. Please continue to submit bugs and feature requests, though it's the community's responsibility to address them.**\n\n.. image:: https://github.com/redcap-tools/PyCap/actions/workflows/ci.yml/badge.svg\n    :target: https://github.com/redcap-tools/PyCap/actions/workflows/ci.yml\n.. image:: https://codecov.io/gh/redcap-tools/PyCap/branch/master/graph/badge.svg?token=IRgcPzANxU\n    :target: https://codecov.io/gh/redcap-tools/PyCap\n.. image:: https://badge.fury.io/py/PyCap.svg\n    :target: https://badge.fury.io/py/PyCap\n.. image:: https://img.shields.io/badge/code%20style-black-black\n    :target: https://pypi.org/project/black/\n.. image:: https://mperlet.github.io/pybadge/badges/10.svg\n    :target: https://pypi.org/project/pylint/\n\nIntro\n=====\n\nPyCap is a python module exposing the REDCap API through some helpful abstractions. Information about the REDCap project can be found at http://project-redcap.org/.\n\nAvailable under the MIT license.\n\nDocumentation\n-------------\n\nCanonical documentation can be found on `ReadTheDocs <http://pycap.rtfd.org>`_.\n\nFeatures\n--------\n\nCurrently, these API calls are available:\n\n-   Export Records\n-   Export Metadata\n-   Import Metadata\n-   Delete Records\n-   Import Records\n-   Export File\n-   Import File\n-   Delete File\n-   Export Users\n-   Export Form Event Mappings\n-   Export Reports\n\nEvents and Arms are automatically exported for longitudinal projects (see below).\n\n\nRequirements\n------------\n\n-   requests (>= 1.0.0)\n\n    ``$ pip install requests``\n\nUsage\n-----\n\n.. code-block:: python\n\n    >>> import redcap\n    # Init the project with the api url and your specific api key\n    >>> project = redcap.Project(api_url, api_key)\n\n    # Export all data\n    >>> all_data = project.export_records()\n\n    # import data\n    >>> data = [{'subjid': i, 'age':a} for i, a in zip(range(1,6), range(7, 13))]\n    >>> num_processed = project.import_records(data)\n\n    # For longitudinal projects, project already contains events, arm numbers\n    # and arm names\n    >>> print project.events\n    ...\n    >>> print project.arm_nums\n    ...\n    >>> print project.arm_names\n    ...\n\n    # Import files\n    >>> fname = 'your_file_to_upload.txt'\n    >>> with open(fname, 'r') as fobj:\n    ...     project.import_file('1', 'file_field', fname, fobj)\n\n    # Export files\n    >>> file_contents, headers = project.export_file('1', 'file_field')\n    >>> with open('other_file.txt', 'w') as f:\n    ...     f.write(file_contents)\n\n    # Delete files\n    >>> try:\n    ...     project.delete_file('1', 'file_field')\n    ... except redcap.RedcapError:\n    ...     # This throws if an error occured on the server\n    ... except ValueError:\n    ...     # This throws if you made a bad request, e.g. tried to delete a field\n    ...     # that isn't a file\n\n    # Delete record\n    >>> response = project.delete_records(['1'])\n\n    # Export form event mappings\n    >>> fem = project.export_instrument_event_mappings()\n    ...\n\n    # Export Reports\n    >>> reports = project.export_report('1')\n\nInstallation\n------------\n\nInstall with :code:`pip`\n\n.. code-block:: sh\n\n    $ pip install PyCap\n\nInstall extra requirements, which allows returning project data as a :code:`pandas.DataFrame`\n\n.. code-block:: sh\n\n    $ pip install PyCap[pandas]\n\nInstall from GitHub\n\n.. code-block:: sh\n\n    $ pip install https://github.com/redcap-tools/PyCap/archive/master.zip\n\n\nContributing\n------------\n\n\n1. Install `poetry <https://python-poetry.org/docs/master/#installation>`_\n\n.. code-block:: sh\n    \n    $ curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -\n\n\n2. Install all project dependencies (including development/optional dependencies).\n\n.. code-block:: sh\n\n    $ poetry install -E data_science\n\n3. Add your changes and make sure your changes pass all tests.\n\n.. code-block:: sh\n\n    $ poetry run pytest\n\nIf you make changes to the dependencies you'll need to handle\nthem with `poetry add/remove <https://python-poetry.org/docs/master/basic-usage/#installing-dependencies>`_\nand update the :code:`requirements.txt` with\n`poetry export <https://python-poetry.org/docs/master/cli/#export>`_ for the CI to run\n(until I figure out the best way to actually run :code:`poetry` in CI)\n\n.. code-block:: sh\n\n    $ poetry export -f requirements.txt --output requirements.txt --dev -E data_science\n\nFinally, start a pull request!\n\nCiting\n------\n\nIf you use PyCap in your research, please consider citing the software:\n\n    Burns, S. S., Browne, A., Davis, G. N., Rimrodt, S. L., & Cutting, L. E. PyCap (Version 1.0) [Computer Software].\n    Nashville, TN: Vanderbilt University and Philadelphia, PA: Childrens Hospital of Philadelphia.\n    Available from https://github.com/redcap-tools/PyCap. doi:10.5281/zenodo.9917\n",
    'author': 'Scott Burns',
    'author_email': 'scott.s.burns@gmail.com',
    'maintainer': 'Paul Wildenhain',
    'maintainer_email': 'pwildenhain@gmail.com',
    'url': 'https://github.com/redcap-tools/PyCap',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
