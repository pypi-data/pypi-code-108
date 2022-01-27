# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['gdphelper']

package_data = \
{'': ['*']}

install_requires = \
['ipykernel>=6.7.0,<7.0.0',
 'matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.22.1,<2.0.0',
 'pandas>=1.3.5,<2.0.0',
 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'gdphelper',
    'version': '0.0.1',
    'description': 'A package for streamlining EDA processes for basic Data Analysis',
    'long_description': "# gdphelper\n\nThis package is designed to take the url of any of the several dozen GDP-related csv datasets from the [Canadian Government Open Data Portal](https://open.canada.ca/en/open-data) and download, clean load, summarize and visualize the data contained within.  \n\nIt contains 4 functions:\n\n`gdpimporter`: Downloads the zipped data, extracts, renames the appropriate csv, and returns a dataframe along with the title from the meta data.    \n`gdpcleaner`: Loads the data, removes spurious columns, renames used columns, scrubs and data issues. Returns a basic data frame and some category flags.   \n`gdpdescribe` : Evaluates the data category and generates summary statistics by year, region, industry, etc.  \n`gdpplotter`: Generates a set of visualizations of the data set according to the user's choices.\n\nThis package is built upon a bunch of popular packages in Python ecosystem, including\n`zipfile`, `matplotlib`, and  `pandas.` What makes this package unique is that it incorporates the common functionalities and streamlines the workflow from downloading the data to performing simple EDA, specifically for the GDP-related data from the Canadian Government Open Data Portal.\n\n## Installation\n\n```bash\n$ pip install git+https://github.com/UBC-MDS/gdphelper\n\n```\n\n## Usage\n\n- TODO\n\n## Contributors\n\n- Aldo Barros          aldosaltao@gmail.com\n- Gabe Fairbrother     gfairbrother@gmail.com\n- Wanying Ye           wanying.ye2020@gmail.com\n- Ramiro Mejia         ramiromejiap@gmail.com\n\n## Contributing\n\nInterested in contributing? Check out the [contributing guidelines](https://github.com/UBC-MDS/Group_03_GOV_CA_GDP_HELPER/blob/main/CONTRIBUTING.md). Please note that this project is released with a [Code of Conduct](https://github.com/UBC-MDS/Group_03_GOV_CA_GDP_HELPER/blob/main/CONDUCT.md). By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`gdphelper` was created by Aldo Barros, Gabriel Fairbrother, Ramiro Mejia, Wanying Ye. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`gdphelper` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n",
    'author': 'Aldo Barros, Gabriel Fairbrother, Ramiro Mejia, Wanying Ye',
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
