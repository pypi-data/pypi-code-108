# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cryptocurrencyeda']

package_data = \
{'': ['*']}

install_requires = \
['altair>=4.2.0,<5.0.0', 'pandas>=1.4.0,<2.0.0', 'pytest>=6.2.5,<7.0.0']

setup_kwargs = {
    'name': 'cryptocurrencyeda',
    'version': '0.2.5',
    'description': 'A package to analyze historical cryptocurrency prices and performance',
    'long_description': '# cryptocurrencyeda\n\nThis is a Python package to analyze historical cryptocurrency prices and performance through simple exploratory data analysis including calculations and plotting. Data is sourced from the KuCoin API. There are four functions that are included in this python package which are described in more detail below. Cryptocurrency investors and enthusiasts can use this package to analyze cryptocurrencies of interest.\n\n\nThere are existing Python libraries to access information of cryptocurrency such as [cryptocompare](https://github.com/lagerfeuer/cryptocompare) and [cryptofeed](https://github.com/bmoscon/cryptofeed). There are also existing Python libraries to visualize financial data such as [mplfinance](https://github.com/matplotlib/mplfinance).\nHowever, there is no integrated Python library for accessing, analyzing, and visualizing cryptocurrency data altogether. Therefore, we want to build a simple tool that can facilitate simple cryptocurrency data analysis all at once.\n\n## Function List\n\nThe package contains the following four functions:\n\n- `retrieve_data`: downloads historical data from a cryptocurrency exchange using an an http request from a cryptocurrency exchange.\n\n- `plot_price`: generates and visualizes a plot of the price of the cryptocurrenty inputted over a period of time.\n\n- `daily_growth_rate`: performs calculation of daily growth rate of the cryptocurrenty inputted over a period of time.\n\n- `avg_daily_return`: performs calculation of the average daily return of the inputted cryptocurrency price.\n## Installation\n\n```bash\n$ pip install cryptocurrencyeda\n```\n\n## Usage\n```Python\nfrom cryptocurrency.retrieve_data import retrieve_data\nfrom cryptocurrency.plot_price import plot_price\nfrom cryptocurrency.avg_daily_return import avg_daily_return\nfrom cryptocurrency.daily_growth_rate import daily_growth_rate\n\nretrieve_data(symbol:str="BTC-USDT",\n                  time_period:str="1day",\n                  start_date:str="2018-01-01",\n                  end_date:str="2022-01-10",\n                 )\n\nplot_price(price_df)\n\ndaily_growth_rate(price_df, closing_price)\n\navg_daily_return(price_df)\n```\n\n## Contributors\n\nWe welcome and recognize all contributions. You can see a list of current contributors in the [`contributors tab`](https://github.com/UBC-MDS/CryptocurrencyEDA/graphs/contributors). If you are interested in contributing to this project, please check out our CONDUCT.md\n\n- Berkay Bulut\n- Cici Du\n- Alex Yinan Guo\n- Nobby Nguyen\n\n## License\n\n`cryptocurrencyeda` was created by MDS Students from Group-11 for course 524. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`cryptocurrencyeda` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Berkay Bulut',
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
