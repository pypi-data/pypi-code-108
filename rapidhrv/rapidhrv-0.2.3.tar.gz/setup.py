# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rapidhrv']

package_data = \
{'': ['*']}

install_requires = \
['dash>=2.0.0,<3.0.0',
 'h5py>=3.3.0,<4.0.0',
 'numpy>=1.21.0,<2.0.0',
 'pandas>=1.3.0,<2.0.0',
 'scikit-learn>=0.24.2,<0.25.0',
 'scipy>=1.7.0,<2.0.0']

extras_require = \
{'notebooks': ['jupyter>=1.0.0,<2.0.0', 'matplotlib>=3.4.2,<4.0.0']}

setup_kwargs = {
    'name': 'rapidhrv',
    'version': '0.2.3',
    'description': 'A package for preprocessing, analyzing and visualizing cardiac data',
    'long_description': '# RapidHRV\n\nRapidHRV is a data processing pipeline for the analysis and visualization of cardiac data.\n\nPlease provide credit where appropriate:\n\nKirk, P. A., Davidson Bryan, A., Garfinkel, S., & Robinson, O. J. (2021).\n_RapidHRV: An open-source toolbox for extracting heart rate and heart rate variability_\n([PsyArXiv](https://doi.org/10.31234/osf.io/3ewgz))\n\nThis library is distributed under an \n[MIT License](https://raw.githubusercontent.com/peterakirk/RapidHRV/main/LICENSE)\n\n## Installation\n\n```shell\npip install rapidhrv\n```\n\n## Usage\n\nGiven a numpy array, or something convertable to it (such as a list),\n`rapidhrv.preprocess` can generate input suitable for analysis with\n`rapidhrv.analyze`, which will return a pandas dataframe containing HRV data.\n\n```python\nimport numpy as np\nimport rapidhrv as rhv\n\nmy_data = np.load("my_data.npy")  # Load data\ndata = rhv.Signal(my_data, sample_rate=50)  # Convert to rhv Signal class\npreprocessed = rhv.preprocess(data)  # Preprocess: may interpolate data, check the docstring on `rapidhrv.preprocess`\nresult = rhv.analyze(preprocessed)  # Analyze signal\n```\n\n## Documentation\n\nPlease see the included [tutorial notebook](https://github.com/peterakirk/RapidHRV/blob/main/resources/tutorial.ipynb).\n\n## Development\n\nIn order to get a working development environment,\nplease install [Poetry](https://python-poetry.org/) for your platform,\nand run `poetry install` to generate a virtual environment.\n\nIf you plan on making any changes to the included notebooks,\nplease run `nbstripout --install` from within the poetry venv before committing any changes.\n\nTo run said notebooks from the environment provided by poetry,\ninstall the required dependencies with `poetry install --extras notebooks`.\n\n',
    'author': 'Peter Kirk',
    'author_email': 'p.kirk@ucl.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
