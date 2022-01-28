# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['covizpy']

package_data = \
{'': ['*']}

install_requires = \
['altair-saver>=0.5.0,<0.6.0', 'altair>=4.2.0,<5.0.0', 'pandas>=1.3.5,<2.0.0']

setup_kwargs = {
    'name': 'covizpy',
    'version': '1.0.2',
    'description': 'Provides access to Covid-19 data from Our World in Data, and functions to generate relevant charts and summaries.',
    'long_description': '# covizpy\n\n[![codecov](https://codecov.io/gh/ubc-mds/covizpy/branch/master/graph/badge.svg)](https://codecov.io/gh/ubc-mds/covizpy)\n[![ci-cd](https://github.com/UBC-MDS/covizpy/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/UBC-MDS/covizpy/actions/workflows/ci-cd.yml)\n[![Documentation Status](https://readthedocs.org/projects/covizpy/badge/?version=latest)](https://covizpy.readthedocs.io/en/latest/?badge=latest)\n\n`covizpy` is a Python package that provides easy access to Covid-19 data from [Our World in Data](https://ourworldindata.org/coronavirus), as well as functions to generate relevant Covid-19 charts and summaries easily. We aim to make `covizpy` simple and easy to use. Our goal is to enable anyone with basic Python programming knowledge to access and visualize Covid-19 data, and make their own informed decisions and conclusions.\n\nThere are existing Python packages that allow users to download and generate Covid-19 charts. For example, [covid19pandas](https://github.com/PayneLab/covid19pandas) is a package that presents COVID-19 data from Johns Hopkins University and The New York Times in pandas dataframes, to make analysis and visualization easier in a Python environment.\n\nWhile other packages have more advanced plotting capabilities, we provide simpler functions that allow users to answer questions regarding the Covid-19 pandemic as quickly as possible.\n\n## Features\n\nThis package contains four functions: `plot_metric`, `plot_spec`, `get_data` and `plot_summary`.\n\n* `plot_metric`: Create a line chart presenting COVID total new cases versus another metric within a time period\n\n* `plot_spec`: Create a line chart presenting specific country/countries COVID information within a time period\n\n* `get_data`: User can retrieve the COVID data from the source as a pandas dataframe. Specific data can be retrieved by passing the date range and the list of countries\n\n* `plot_summary`: Create a horizontal bar chart summarising a specified variable and value within a time period\n\n## Dependencies\n\nBefore installing the package, following packages must be installed:\n\n- python = "^3.9"\n- pandas = "^1.3.5"\n- altair = "^4.2.0"\n- altair-saver = "^0.5.0"\n\n## Installation\n\n```bash\npip install --index-url https://test.pypi.org/simple/ covizpy\n```\n\n## Usage and Examples\n\nTo use the package, import the package with following commands:\n\n```python\nfrom covizpy.get_data import get_data\nfrom covizpy.plot_summary import plot_summary\nfrom covizpy.plot_metric import plot_metric\nfrom covizpy.plot_spec import plot_spec\n```\n\nTo use the functions, see below examples:\n\n### Retrieve COVID-19 data with specified date range and default all locations\n\n```python\ndf = get_data(date_from="2022-01-01", date_to="2022-01-21")\n```\n\n### Plot summary graph (bar chart)\n\n```python\nplot_summary(df, var="location", val="new_cases", fun="sum", date_from="2022-01-01", date_to="2022-01-15", top_n=10)\n```\n\n![Summary graph](https://github.com/UBC-MDS/covizpy/raw/main/img/plot_summary.png)\n\n### Plot COVID-19 cases for specific countries (line chart)\n\n```python\nplot_spec(df, location=["Canada", "Turkey"], val="new_cases", date_from="2022-01-01", date_to="2022-01-07")\n```\n\n![New COVID-19 specific graph](https://github.com/UBC-MDS/covizpy/raw/main/img/plot_spec.png)\n\n### Plot new COVID-19 cases versus another metric (line chart)\n\n```python\nplot_metric(metric=\'positive_rate\', date_from="2022-01-15", date_to="2022-01-21")\n```\n\n![New COVID-19 case metric graph](https://github.com/UBC-MDS/covizpy/raw/main/img/plot_metric.png)\n\n\n\n\n## Contributors\n\n* Rohit Rawat\n* Rong Li\n* Thomas Siu\n* Ting Zhe Yan\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`covizpy` was created by Rohit Rawat, Rong Li, Thomas Siu, Ting Zhe Yan. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`covizpy` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Rohit Rawat, Rong Li, Thomas Siu, Ting Zhe Yan',
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
