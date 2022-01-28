# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['py_outliers_utils']

package_data = \
{'': ['*']}

install_requires = \
['altair>=4.2.0,<5.0.0', 'pandas>=1.4.0,<2.0.0']

setup_kwargs = {
    'name': 'py-outliers-utils',
    'version': '1.2.5',
    'description': 'Dealing with outliers',
    'long_description': '# py_outlier_utils \n\n[![ci-cd](https://github.com/UBC-MDS/py_outliers_utils/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/UBC-MDS/py_outliers_utils/actions/workflows/ci-cd.yml)\n\n## Overview\nAs data rarely comes ready to be used and analyzed for machine learning right away, this package aims to help speed up the process of cleaning and doing initial exploratory data analysis specific to outliers. The package focuses on the tasks of identifying univariate outliers, providing summary of outliers like count, range of outliers, visualize them and giving functionality to remove them from data.\n\n## Installation\n\n```bash\n$ pip install py_outlier_utils\n```\n\n## Functions\nThe three functions contained in this package are as follows:\n\n- `outlier_identifier`: A function to identify outliers in the dataset and provide their summary as an output\n- `visualize_outliers`: A function to generate the eda plots highlighting outliers providing additional functionality to visualize them\n- `trim_outliers`: A function to generate outlier free dataset by imputing them with mean, median or trim entire row with outlier from dataset.\n\n## Our Place in the Python Ecosystem\nWhile Python packages with similar functionalities exist, this package aims to provide summary, visualization of outliers in a single package with an additional functionality to generate outlier-free dataset. Few packages with similar functionality are as follows:\n\n- [pyod](https://pypi.org/project/pyod/)\n- [python-outlier](https://pypi.org/project/python-outlier/)\n\n## Usage\n\n`py_outlier_utils` can be used to deal with the outliers in a dataset and plot the distribution of the dataset. More information can be found in [Example usage](https://py-outliers-utils.readthedocs.io/en/latest/example.html).\n\n## Contributing\n\nThis package is authored by Karanpreet Kaur, Linhan Cai, Qingqing Song as part of the course project in DSCI-524 (UBC-MDS program). You can see the list of all contributors in the contributors tab.\n\nWe welcome and recognize all contributions. If you wish to participate, please review our [Contributing guidelines](CONTRIBUTING.md)\n\n## License\n\n`py_outlier_utils` is licensed under the terms of the MIT license.\n\n## Credits\n\n`py_outlier_utils` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'scarlqq',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
