# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['slimeda']

package_data = \
{'': ['*']}

install_requires = \
['altair>=4.2.0,<5.0.0', 'numpy>=1.22.1,<2.0.0', 'pandas>=1.3.5,<2.0.0']

setup_kwargs = {
    'name': 'slimeda',
    'version': '0.1.1',
    'description': 'Slim version of EDA processing Python package',
    'long_description': "# slimeda\n\nExploratory Data Analysis is an important preparatory work to help data scientists understand and clean up data sets before machine learning begins. However, this step also involves a lot of repetitive tasks. In this context, slimeda will help data scientists quickly complete the initial work of EDA and gain a preliminary understanding of the data.\n\nSlimeda focuses on unique value and missing value counts, as well as making graphs like histogram and correlation graphs. Also, the generated results are designed as charts or images, which will help users more flexibly reference their EDA results.\n\n## Function Specification\n\nThe package is under developement and includes the following functions:\n\n- **histogram** : This function accepts a dataframe and builds histograms for all numeric columns which are returned \nas an array of chart objects. The user has the option to save the image to path.\n\n- **corr_map** : This function accepts a dataframe and builds an heat map for all numeric columns which is returned \nas a chart object. The user has the option to save the image to path.\n\n- **cat_unique_count** : This function accepts a dataframe and returns a table of unique value counts for all categorical columns.\n\n- **miss_counts** : This function accepts a dataframe and returns a table of counts of missing values in all columns.\n\nLimitations:\nWe only consider numeric and categorical columns in our package.\n\n## Installation\n\n```bash\n$ pip install git+https://github.com/UBC-MDS/slimeda\n```\n## Usage\n\n- To do (will complete this part in milestone2)\n\n\n## Fitting in Python Ecosystem\n- Packages have similar functions are:\n    -  [numpy](https://numpy.org/): can count unique value and missing value\n    - [pandas-profiling](https://pandas-profiling.github.io/pandas-profiling/docs/master/rtd/): can generate basic eda reports.\n- Slimeda's innovation points:\n\n    - We aggregate necessary functions for eda in one function that can only be done with multiple packages and simplify the code. For example, for missing value counts, we not only get the counts but also calculate its percentage.\n    - Compared with numpy, we optimize the output to be more clear.\n    - Compared with pandas-profiling, we generate the most commonly used graphs and make possible for png outputs, which is much more flexible for users to get their eda results.\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## CONTRIBUTORS\n\nGroup 4 members:\n- Khalid Abdilahi (@khalidcawl)\n- Anthea Chen (@anthea98)\n- Simon Guo (@y248guo)\n- Taiwo Owoseni (@thayeylolu)\n\n\n## License\n\n`slimeda` was created by Simon Guo. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`slimeda` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n",
    'author': 'Simon Guo',
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
