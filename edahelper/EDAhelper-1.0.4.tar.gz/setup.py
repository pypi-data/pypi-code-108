# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['EDAhelper']

package_data = \
{'': ['*']}

install_requires = \
['altair>=4.2.0,<5.0.0']

setup_kwargs = {
    'name': 'edahelper',
    'version': '1.0.4',
    'description': 'Toolset to make EDA easier!',
    'long_description': '# EDAhelper\n[![Documentation Status](https://readthedocs.org/projects/edahelper/badge/?version=latest)](https://edahelper.readthedocs.io/en/latest/?badge=latest)\n[![codecov](https://codecov.io/gh/UBC-MDS/EDAhelper/branch/master/graph/badge.svg?token=2aRO8HaPHn)](https://codecov.io/gh/UBC-MDS/EDAhelper)\n![github workflow](https://github.com/UBC-MDS/EDAhelper/actions/workflows/ci-cd.yml/badge.svg)\n\nTools to make EDA easier!\n\n## About\n\nThis package is aimed at making the EDA process more effective. Basically, we found there were tons of repetitive work when getting a glimpse of the data set. To stop wasting time in repeating procedures, our team came up with the idea to develop a toolkit that includes the following functions:\n\n  1. Clean the data and replace missing values by using the method preferred.\n  2. Provide the description of the data such as the distribution of each column of the data.\n  3. Give the correlation plot between different numeric columns automatically.\n  4. Combine the plots and make them suitable for the report.\n\n## Contributors\n\n- Rowan Sivanandam\n- Steven Leung\n- Vera Cui\n- Jennifer Hoang\n\n## Feature specifications\n\n  1. `preprocess(path, method=None, fill_value=None, read_func=pd.read_csv, **kwarg)` : <br>\n  The function is to preprocess data in txt or csv by dealing with missing values. There are 5 imputation methods provided (None, \'most_frequent\', \'mean\', \'median\', \'constant\'). Finally, it will return the processed data as pandas.DataFrame.\n  2. `column_stats(data, column1, column2 = None, column3 = None, column4 = None)` : <br>\n  The function is to obtain summary statistics of column(s) including count, mean, median, mode, Q1, Q3, variance, standard deviation, correlation. Finally, it will return summary table detailing all statistics and correlations between chosen columns.\n  3. `plot_histogram(data, columns=["all"], num_bins=30)`: : <br>\n  The function is to create histograms for numerical features within a dataframe using Altair. Finally, it will return an Altair plot for each specified continuous feature.\n  4. `numeric_plots(df)` : <br>\n  The function takes a dataframes and plot the possible pairs of the numeric columns using Altair, creating a matrix of correlation plots.\n\n  \n## Related projects\n\nSurely, EDA is not a new topic to data scientists. There are quite a few packages doing similar work on PyPI. However, most of them only include limited functions like just providing descriptive statistics. Our proposal is more of a one-in-all toolkit for EDA. Below is a list of sister-projects.\n\n- [auto-eda](https://pypi.org/project/auto-eda/) : It is an automatic script that generating information in the dataset.\n- [easy-eda](https://pypi.org/project/easy-eda/) : Exploratory Data Analysis.\n- [quick-eda](https://pypi.org/project/quick-eda/) : Important dataframe statistics with a single command.\n- [eda-report](https://pypi.org/project/eda-report/) : A simple program to automate exploratory data analysis and reporting.\n\n## Installation\n\nYou can also use Git to clone the repository from GitHub to install the latest development version:\n```bash\n$ git clone https://github.com/UBC-MDS/EDAhelper.git\n$ cd dist\n$ pip install EDAhelper-3.0.0-py3-none-any.whl\n```\nor install from `PyPI`:\n```bash\n$ pip install edahelper\n```\n\n## Usage\n\nExample usage:\n```python\nfrom EDAhelper import EDAhelper\nEDAhelper.preprocess(\'file_path\')\nEDAhelper.column_stats(df, columns = (\'Date\', PctPopulation\', \'CrimeRatePerPop\'))\nEDAhelper.plot_histogram(df, columns = [\'A\', \'B\'])\nEDAhelper.numeric_plot(df) \n```\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`EDAhelper` was created by Rowan Sivanandam, Steven Leung, Vera Cui, Jennifer Hoang. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`EDAhelper` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Rowan Sivanandam, Steven Leung, Vera Cui, Jennifer Hoang',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/UBC-MDS/EDAhelper.git',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
