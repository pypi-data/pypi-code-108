# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tensorvis', 'tensorvis.utils']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.0,<9.0.0',
 'kaleido>=0.2.1,<0.3.0',
 'pandas>=1.1.4,<2.0.0',
 'plotly>=4.14.3,<5.0.0',
 'tensorboard>=2.4.0,<3.0.0']

entry_points = \
{'console_scripts': ['tensorvis = tensorvis.vis:cli']}

setup_kwargs = {
    'name': 'tensorvis',
    'version': '1.2.6',
    'description': 'Visualisation tool to support my PhD automating the process of gathering data and plotting it',
    'long_description': '\n<h1 align="center">\nTensorVis\n</h1>\n\n<p align="center">\n  <a href="http://makeapullrequest.com">\n    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg">\n  </a>\n  <a href="https://github.com/npitsillos/tensorplot/issues"><img src="https://img.shields.io/github/issues/npitsillos/tensorplot.svg"/></a>\n\n  <a href="https://github.com/ambv/black">\n    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style: Black">\n  </a>  \n</p>\n\n<p align="center">\n<a href="#overview">Overview</a>\n•\n<a href="#features">Features</a>\n•\n<a href="#installation">Installation</a>\n•\n<a href="#contribute">Contribute</a>\n</p>\n\n# Overview\nA command line tool to automate the process of grabbing tensorboard events data and visualising them.  This allows for faster result analysis and separation of the experiment logic from the visualisation aspect of the metrics logged in tensorboard.\n\n# Features\n* Uploads experiment metrics logged to tensorboard to tensorboard.dev and creates a log of uploaded experiments.\n* Downloads experiments from tensorboard.dev to a local csv file.\n* Plots experiment metrics.\n\n## Benefits\n1. Faster result analysis\n2. Less code writting\n3. Separate experiments from analysis\n4. Allows for more research time\n\n# Installation\n```tensorvis``` can be installed using pip with the command:\n\n```\npip install tensorvis\n```\n\nThis will install ```tensorvis``` in the current python environment and will be available through the terminal.\n\n## Assumptions\nThere can be many different directory structures when running and logging experiments with tensorboard.  This tool makes several assumptions to make it easier to handle dataframes resulting from downloading experiments.\n\n```tensorvis``` assumes the following directory structure of tensorboard logs within the top level directory ```logs```, where each ```run``` subdirectory contains the events file:\n\n```bash\nlogs\n├── exp_name_1\n│\xa0\xa0 ├── run_1\n│\xa0\xa0 └── run_2\n├── exp_name_2\n│\xa0\xa0 ├── run_1\n│\xa0\xa0 ├── run_2\n│\xa0\xa0 └── run_3\n└── exp_name_3\n    └── run_1\n```\n\n> For a description of how the directory structure is represented in a dataframe follow this [link](https://www.tensorflow.org/tensorboard/dataframe_api#loading_tensorboard_scalars_as_a_pandasdataframe).\n\nBy default ```tensorvis``` assumes a single experiment directory is provided which corresponds to a single experiment having multiple runs.  All runs from a single experiment will be aggregate and averaged to plot the mean values along with the standard deviation.\n\n# Contribute\nAny feedback on ```tensorvis``` is welcomed in order to improve its usage and versatility.  If you have something specific in mind please don\'t hesitate to create an issue or better yet open a PR!\n\n## Current Contributors\n* [npitsillos](https://github.com/npitsillos)',
    'author': 'Nikolas Pitsillos',
    'author_email': 'npitsillos@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/npitsillos/tensorplot.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
