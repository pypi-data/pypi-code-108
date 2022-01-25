# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['mapstp', 'mapstp.cli', 'mapstp.utils']

package_data = \
{'': ['*'], 'mapstp': ['data/*']}

install_requires = \
['click>=8.0.1,<9.0.0',
 'numpy>=1.21.4,<2.0.0',
 'openpyxl>=3.0.9,<4.0.0',
 'pandas>=1.3.4,<2.0.0',
 'tomli>=1.2.1,<2.0.0']

entry_points = \
{'console_scripts': ['mapstp = mapstp.cli.runner:mapstp']}

setup_kwargs = {
    'name': 'mapstp',
    'version': '0.3.1',
    'description': 'Transfers meta information from STP to MCNP',
    'long_description': '==========================================================\n*mapstp*: link STP and MCNP models\n==========================================================\n\n|Maintained| |License| |Versions| |PyPI| |Docs|\n\n\n.. contents::\n\n\nDescription\n-----------\n\nProblem #1\n~~~~~~~~~~\n\nYou are an MCNP model developer. You have created simplified 3D CAD model using SpaceClaim, saved it to STP file, then converted\nit using SuperMC to an MCNP model. At this moment the MCNP model doesn\'t have any information on relation of the MCNP\ncame from cells to the CAD components, there\'s no materials and densities in the cell specifications.\nThe SuperMC (for the time of writing this) doesn\'t transfer this information on exporting to MCNP model.\n\nProblem #2\n~~~~~~~~~~\n\nYou have to provide results of neutron analysis in correspondence with 3D CAD model\ncomponents. For example, you have to create a table describing activation of every component.\nTo do this, you need some tools to associate CAD component with corresponding MCNP cells.\nUsing this table the results of computation for MCNP cells can be aggregated to values for\ncorresponding CAD component.\n\n\nSolution\n~~~~~~~~\n\nUsing SpaceClaim you can add additional properties to components directly in STP file.\nThe properties include: used material, density correction factor, classification tag.\nThe properties are specified as a special label, which you can add to the components names.\nThe properties are propagated over the CAD tree hierarchy from top to down and can be overridden\non lower levels with more specific values. Using SpaceClaim for this is rather intuitive.\n\nThe using *mapstp* you can transfer this information from STP to MCNP:\nThe  *mapstp*:\n\n* sets material numbers and densities in all the cells, where it was specified\n* adds $-comment after each cell denoting its path in STP, with tag "stp:",this lines can be easily removed later, if not needed\n* adds materials specifications, if they are available for *mapstp*\n* creates separate accompanying excel file with list of cells, applied materials, densities and correction factors, classification tag, and paths in STP\n\n\nInstallation\n------------\n\nDocumentation\n-------------\n\nContributing\n------------\n\n.. image:: https://github.com/MC-kit/map-stp/workflows/Tests/badge.svg\n   :target: https://github.com/MC-kit/map-stp/actions?query=workflow%3ATests\n   :alt: Tests\n.. image:: https://codecov.io/gh/MC-kit/map-stp/branch/master/graph/badge.svg?token=wlqoa368k8\n  :target: https://codecov.io/gh/MC-kit/map-stp\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n.. image:: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336\n   :target: https://pycqa.github.io/isort/\n.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n\n\n\n.. Substitutions\n\n.. |Maintained| image:: https://img.shields.io/badge/Maintained%3F-yes-green.svg\n   :target: https://github.com/MC-kit/map-stp/graphs/commit-activity\n.. |Tests| image:: https://github.com/MC-kit/map-stp/workflows/Tests/badge.svg\n   :target: https://github.com/MC-kit/map-stp/actions?workflow=Tests\n   :alt: Tests\n.. |License| image:: https://img.shields.io/github/license/MC-kit/map-stp\n   :target: https://github.com/MC-kit/map-stp\n.. |Versions| image:: https://img.shields.io/pypi/pyversions/mapstp\n   :alt: PyPI - Python Version\n.. |PyPI| image:: https://img.shields.io/pypi/v/mapstp\n   :target: https://pypi.org/project/mapstp/\n   :alt: PyPI\n.. |Docs| image:: https://readthedocs.org/projects/mapstp/badge/?version=latest\n   :target: https://mapstp.readthedocs.io/en/latest/?badge=latest\n   :alt: Documentation Status\n',
    'author': 'dvp',
    'author_email': 'dmitri_portnov@yahoo.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MC-kit/map-stp',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
