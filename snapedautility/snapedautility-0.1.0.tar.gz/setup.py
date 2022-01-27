# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['snapedautility']

package_data = \
{'': ['*']}

install_requires = \
['altair>=4.2.0,<5.0.0',
 'numpy>=1.22.1,<2.0.0',
 'palmerpenguins>=0.1.4,<0.2.0',
 'pandas>=1.3.5,<2.0.0']

setup_kwargs = {
    'name': 'snapedautility',
    'version': '0.1.0',
    'description': 'A package for doing great things!',
    'long_description': '# snapedautility\n\nsnapedautility is an open-source library that generate useful function to kickstart EDA (Exploratory Data Analysis) with just a few lines of code. The system is built around quickly **analyzing the whole dataset** and **providing a detailed report with visualization**. Its goal is to help quick analysis of feature characteristics, detecting outliers from the observations and other such data characterization tasks.\n## Features\n1. `plot_histograms`: Plots the distribution for numerical, categorical and text features\n2. `detect_outliers`: Generate a violin plot that indicates the outliers that deviate from other observations on data.\n3. `plot_corr`: Generates Correlation Plots for numerical (Pearson\'s correlation), categorical (uncertainty coefficient) and categorical-numerical (correlation ratio) datatypes seamlessly for all data types.\n## Installation\n\n```bash\n$ pip install snapedautility\n```\n\n## Usage\n\n### plot_histograms\n```\n>>> from snapedautility.plot_histograms import plot_histograms\n>>> df = penguins_data\n>>> plot_histograms(df, ["Culmen Length (mm)", "Culmen Depth (mm)", \'Species\'], 100, 100)\n```\n\n### plot_corr\n```\n>>> from snapedautility.plot_corr import plot_corr\n>>> df = penguins_data\n>>> plot_corr(df, ["Culmen Length (mm)", "Culmen Depth (mm)", \'Species\'])\n```\n\n### detect_outliers\n```\n>>> from snapedautility.detect_outliers import detect_outliers \n>>> s = pd.Series([1,1,2,3,4,5,6,9,10,13,40])\n>>> detect_outliers(s)\n```\n\n## Contributors\n\n|  \t Core contributor| Github.com username| \n|---------|---|\n|  Kyle Ahn |  @AraiYuno | \n|  Harry Chan |  @harryyikhchan | \n|  Dongxiao Li | @dol23asuka | \n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## Similar Work\n\nWe recognize EDA (exploratory data analysis) and preprocessing packages are common in the Python open source ecosystem. Our package aims to do a few things very well, and be light weight. A non exhaustive list of EDA helper packages in Python include:\n\n- [`pandasprofiling`](https://github.com/pandas-profiling/pandas-profiling)\n    - This was the original inspiration for this project. We would like to expand the functionalities on this project.\n- [`sweetviz`](https://github.com/fbdesignpro/sweetviz)\n    - This package produces very clean visuals detailing breakdowns in descriptive statistics and can do so with train/test sets for model building workflows.\n- [`ExploriPy`](https://github.com/exploripy/exploripy)\n    - This packages does the most common EDA tasks but also adds in the ability to do statistical testing using analysis of variance (ANOVA), Chi Square test of independence etc.\n\n## License\n\n`snapedautility` was created by Kyle Ahn, Harry Chan and Dongxiao Li. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`snapedautility` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Kyle Ahn',
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
