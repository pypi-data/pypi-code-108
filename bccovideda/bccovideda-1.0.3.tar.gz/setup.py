# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['bccovideda']

package_data = \
{'': ['*']}

install_requires = \
['altair-saver>=0.5.0,<0.6.0',
 'altair>=4.2.0,<5.0.0',
 'ipykernel>=6.7.0,<7.0.0',
 'pandas>=1.3.5,<2.0.0',
 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'bccovideda',
    'version': '1.0.3',
    'description': 'A package to download BC covid data and create simple EDA',
    'long_description': '[![ci-cd](https://github.com/UBC-MDS/bccovideda/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/UBC-MDS/bccovideda/actions/workflows/ci-cd.yml)\n[![codecov](https://codecov.io/github/UBC-MDS/bccovideda/branch/main/graph/badge.svg)](https://codecov.io/github/UBC-MDS/bccovideda)\n# bccovideda\n\n**Authors**:  Lianna Hovhannisyan, John Lee, Vadim Taskaev, Vanessa Yuen\n\nThe British Columbia Center for Disease Control (BCCDC) manages a range of provincial programs and clinics that contribute to public health and help control the spread of disease in BC. It administers and distributes the latest daily data on COVID-19 in British Columbia, which it provides in csv format along case-, lab- and regional-specific features as well as in comprehensive ArcGIS format via the [COVID-19 webpage](http://www.bccdc.ca/health-info/diseases-conditions/covid-19/data) (under "Download the data"). This package leverages daily case-specific COVID-19 data, allowing users to conveniently download the latest case data, and - per specified date range interval - compute several key statistics, visualize time series progression along age-related and regional parameters, and generate exploratory data analysis in the form of histogram figures supporting on-demand analysis. COVID-19 case detail parameters extracted using this package: \n- Reported_Date (in YYYY-MM-DD format)\n- HA (provincial health region, e.g., "Vancouver Coast Health")\n- Sex (M or F)\n- Age_Group (reported along 10-yr age group bins, e.g., "60-69")\n- Classification_Reported (diagnosis origin, e.g., "Lab-diagnosed")\n\n## Installation\n\n`bccovideda` can be installed from PyPI using the following terminal command:\n```bash\n$ pip install bccovideda\n```\n\n`bccovideda` can be used to download and compute summary statistics, generate exploratory data analysis histogram plots, and plot time series chart data as follows:\n```python\nfrom bccovideda.get_data import get_data\nfrom bccovideda.show_summary_stat import show_summary_stat\nfrom bccovideda.plot_hist_by_cond import plot_hist_by_cond\nfrom bccovideda.plot_line_by_date import plot_line_by_date\n\nNote: If this package is to be installed in virtual environment, `poetry install` is required to run pytest.\n\nbccovideda.show_summary_stat("2022-01-01", "2022-01-13")\nbccovideda.plotHistByCond("2021-01-01", "2021-12-31", "Age")\nbccovideda.plotLineByDate("2021-01-01", "2021-12-31", region = [\'Fraser\'])\n```\n\n## Package Functions \n\n- `get_data()`\n  - This function downloads the latest detailed daily case-specific COVID-19 from BCCDC\'s dedicated [COVID-19 homepage](http://www.bccdc.ca/health-info/diseases-conditions/covid-19/data). It returns a dataframe containing the extracted raw data. \n\n- `show_summary_stat()`\n  - This function computes summary statistics from the available case-specific parameters, such as age-related and regional aggregate metrics. It returns a dataframe listing key identified summary statistics specified per the time interval queried. \n\n- `plot_line_by_date()`\n  - This function returns a line chart plot of daily case counts, based on parameters and grouping selected by the user, per the time interval queried.\n\n- `plot_hist_by_cond()`\n  - This function returns a histogram plot based on parameters and grouping selected by the user, per the time interval queried, allowing for on-demand exploratory data analysis. \n\n\n## Usage\n\n## Role within Python Ecosystem\n\nGiven the relatively adequate accessibility of latest aggregate COVID-19 data combined with its persistent impact on socio-economics since early 2020, there are a number of rather comprehensive Python packages that perform similar data extract and exploratory data analysis functions, such as [covid](https://pypi.org/project/covid/), [covid19pyclient](https://pypi.org/project/covid19pyclient/), [covid19pandas](https://github.com/PayneLab/covid19pandas). In contrast to existing packages, `bccovideda` provides a simple user interface that  focuses on the localized provincial context of British Columbia, utilizing features specific to BCCDC\'s data administration conventions for generating a quick overview and on-demand analysis of trends and statistics pertaining to age-related and regional case characteristics.\n\n## Dependencies\n\n-   Python 3.9 and Python packages:\n\n    -   pandas==1.3.5\n    -   requests==2.27.1\n    -   altair==4.2.0\n    -   altair-saver==0.5.0\n\n## Documentation\n\nDocumentation `bccovideda` can be found at [Read the Docs]()\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## Contributors\n\nGroup 25 Contributors:\n- Lianna Hovhannisyan: @liannah\n- John Lee: @johnwslee\n- Vadim Taskaev: @vtaskaev1\n- Vanessa Yuen: @imtvwy\n\n## License\n\nThe `bccovideda` project was created by DSCI 524 (Collaborative Software Development) Group 25 within the Master of Data Science program at the University of British Columbia (2021-2022). It is licensed under the terms of the MIT license.\n\n## Credits\n\n`bccovideda` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'MDS 2021 DSCI 524 Group 25',
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
