# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['entropylab',
 'entropylab.api',
 'entropylab.cli',
 'entropylab.instruments',
 'entropylab.results.dashboard',
 'entropylab.results_backend',
 'entropylab.results_backend.sqlalchemy',
 'entropylab.results_backend.sqlalchemy.alembic',
 'entropylab.results_backend.sqlalchemy.alembic.versions']

package_data = \
{'': ['*'], 'entropylab.results.dashboard': ['assets/*', 'assets/images/*']}

install_requires = \
['alembic>=1.6.5,<2.0.0',
 'bokeh>=2.3.0,<3.0.0',
 'dash-bootstrap-components>=1.0.0,<2.0.0',
 'dash>=2.0.0,<3.0.0',
 'dill>=0.3.3,<0.4.0',
 'dynaconf>=3.1.4,<4.0.0',
 'graphviz>=0.16,<0.17',
 'h5py>=3.3.0,<4.0.0',
 'jsonpickle>=2.0.0,<3.0.0',
 'matplotlib>=3.4.1,<4.0.0',
 'networkx>=2.5.1,<3.0.0',
 'numpy>=1.20.1,<2.0.0',
 'pandas>=1.2.3,<2.0.0',
 'param>=1.10.1,<2.0.0',
 'sqlalchemy>=1.4.0,<2.0.0',
 'waitress>=2.0.0,<3.0.0']

entry_points = \
{'console_scripts': ['entropy = entropylab.cli.main:main',
                     'n3p = entropylab.cli.main:main']}

setup_kwargs = {
    'name': 'entropylab',
    'version': '0.4.1',
    'description': '',
    'long_description': '![PyPI](https://img.shields.io/pypi/v/entropylab)\n[![discord](https://img.shields.io/discord/806244683403100171?label=QUA&logo=Discord&style=plastic)](https://discord.gg/7FfhhpswbP)\n\n[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)\n[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4785097.svg)](https://doi.org/10.5281/zenodo.4785097)\n\n# Entropy\n\nEntropy is a lab workflow managment package built for, but not limitied-to, streamlining the process of running quantum information processing experiments. \n\nEntropy is built to solve a few major hurdles in experiment design: \n\n1. Building, maintaining and executing complex experiments\n2. Data collection\n3. Device management\n4. Calibration automation\n\nTo tackle these problems, Entropy is built around the central concept of a graph strucutre. The nodes of a graph give us a convenient way \nto brake down experiments into stages and to automate some of the tasks required in each node. For example data collection is automated, at least in part, \nby saving node data and code to a persistant database. \n\nDevice managment is the challange of managing the state and control of a variety of different resources. These include, but are not limited to, lab instrumnets. \nThey can also be computational resources, software resources or others. Entropy is built with tools to save such resources to a shared database and give nodes access to \nthe resources needed during an experiment. \n\nPerforming automatic calibration is an important reason why we built Entropy. This could be though of as the usecase most clearly benefiting from shared resources, persistant \nstorage of different pieced of information and the graph structure. If the final node in a graph is the target experiment, then all the nodes between the root and that node are often \ncalibration steps. The documentation section will show how this can be done. \n\nThe Entropy system is built with concrete implemnetations of the various parts (database backend, resource managment and others) but is meant to be completely customizable. Any or every part of the system can be tailored by end users. \n\n## Versioning and the Alpha release \n\nThe current release of Entropy is version 0.1.0. You can learn more about the Entropy versioning scheme in the versioning\ndocument. This means this version is a work in progress in several important ways: \n\n1. It is not fully tested\n2. There are important features missing, such as the results GUI which will enable visual results viewing and automatic plotting\n3. There will more than likely be breaking changes to the API for a while until we learn how things should be done. \n\nKeep this in mind as you start your journey. \n\n## Installation\n\nInstallation is done from pypi using the following command\n\n```shell\npip install entropylab\n```\n\n## Testing your installation\n\nimport the library from `entropylab`\n\n```python\nfrom entropylab import *\n\ndef my_func():\n    return {\'res\': 1}\n\nnode1 = PyNode("first_node", my_func, output_vars={\'res\'})\nexperiment = Graph(None, {node1}, "run_a")  # No resources used here\nhandle = experiment.run()\n```\n\n## Usage\n\nSee [docs](docs) folder in this repository for all the dirty details.\n\n\n## Extensions\n\nEntropy can and will be extended via custom extensions. An example is `entropylab-qpudb`, an extension built to keep track of the calibration parameters of a mutli-qubit Quantum Processing Unit (QPU). This extension is useful when writing an automatic calibration graph. \n\n\n\n',
    'author': 'Guy Kerem',
    'author_email': 'guy@quantum-machines.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/entropy-lab/entropy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
