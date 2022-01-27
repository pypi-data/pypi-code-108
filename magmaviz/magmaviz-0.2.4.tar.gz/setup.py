# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['magmaviz']

package_data = \
{'': ['*']}

install_requires = \
['altair>=4.2.0,<5.0.0', 'pandas>=1.3.5,<2.0.0', 'vega-datasets>=0.9.0,<0.10.0']

setup_kwargs = {
    'name': 'magmaviz',
    'version': '0.2.4',
    'description': 'This package contains four different data visualization functions with the magma theme for EDA.',
    'long_description': '# magmaviz\n\nExploratory Data Analysis is one of the key steps in a machine learning project. This package aims to make this process easy by providing python functions based on the \'Altair\' package to plot four common types of plots with the magma color scheme. To maximize interpretability, the plots have defined color schemes (discrete, diverging, sequential) based on the kind of data they show.\n\n## Installation\n\n```bash\n$ pip install -i https://test.pypi.org/simple/ magmaviz\n```\n\n## Usage\n\nThis package defines four data visualization functions, all with a magma color scheme. They are meant to be used in any data analysis projects using Python. \n\n### Boxplot\n\nReturns a boxplot based on a data frame, a numerical feature to view the distribution of and a categorical feature to bucket data into categories. Additionally, there is a boolean option to facet the boxplots into separate charts.\n\n```python\nfrom magmaviz.boxplot import boxplot\nboxplot(df, x, y, facet=False)\n```\n\n### Correlation Plot\n\nReturns a correlation plot based on the numerical features present in the data frame. While the default plot would use circle shapes, an auxiliary input provides the flexibility to switch to square shapes. Additionally, it will print the correlated numerical feature pairs along with their correlation values.\n\n```python\nfrom magmaviz.corrplot import corrplot\ncorrplot(df, print_corr=True, shape="square")\n```\n\n### Histogram\n\nReturns a histogram based on the data frame and a categorical feature to plot on the x-axis. The y-axis will display the result of some of the following aggregating functions:\n- Average\n- Count\n- Distinct\n- Max\n- Min\n- Median\n- Mean\n- Among others (listed in documentation for the function).\n\n```python\nfrom magmaviz.histogram import histogram\nhistogram(mtcars, "cars", "count()")\n```\n\n### Scatterplot\n\nReturns a scatterplot based on the data frame and two numerical feature names passed as the required inputs. There are auxiliary inputs that provide the flexibility to:\n- Color code or change the shape of the data points on a categorical variable\n- Set a title to the plot, x-axis, y-axis and color legend\n- Change the opacity and size of the data points\n- Set the scale of the x-axis and y-axis to start from zero\n\n```python\nfrom magmaviz.scatterplot import scatterplot\nscatterplot(df, x, y, c="", t="", o=1.0, s=50, xtitle="", ytitle="", ctitle="", xzero=False, yzero=False, shapes=True)\n```\n\n### Fit within the Python ecosystem\n\nOur package will build onto the existing features of \'Altair\' using the magma color scheme. It serves as an automated plotter and is a higher level implementation of it. Essentially it circumvents the need to code every single detail and allows the user to focus on the output. We came across two packages that have a similar line of thought:\n\n- [deneb](https://pypi.org/project/deneb/) (Altair) - uses the same base as this package\n- [spartan-viz](https://pypi.org/project/spartan-viz/) (Matplotlib) - same philosophy as this package: focus on good use of color\n\n\n## Contributing\n\nThe primary contributors to this package are:\n\n1. Abdul Moid Mohammed\n2. Mukund Iyer\n3. Irene Yan\n4. Rubén De la Garza Macías\n\nWe welcome new ideas and contributions. Please refer to the contributing guidelines in the CONTRIBUTING.MD file. Do note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`magmaviz` was created by Abdul Moid Mohammed, Mukund Iyer, Irene Yan, Rubén De la Garza Macías. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`magmaviz` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Abdul Moid Mohammed, Mukund Iyer, Irene Yan, Rubén De la Garza Macías',
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
