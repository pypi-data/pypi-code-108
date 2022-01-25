# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['planetwatch']

package_data = \
{'': ['*']}

install_requires = \
['attr',
 'click',
 'millify>=0.1.1,<0.2.0',
 'pandas',
 'py-algorand-sdk==1.9.0b2',
 'pycoingecko>=2.2.0,<3.0.0',
 'streamlit>=0.88.0']

entry_points = \
{'console_scripts': ['planets = planetwatch.core:cli']}

setup_kwargs = {
    'name': 'planetwatch',
    'version': '0.1.9',
    'description': 'Code to make it easy to calculate earnings, etc for planetwatch',
    'long_description': '# planetwatch\nCode to make it easier to figure out earnings and taxes for planetwatch\n\n\n## Install\nClone the repo, install python 3.7 or greater, and then install.\n\n```\ngit clone https://github.com/errantp/planetwatch.git\ncd planetwatch\npip install .\n\n```\n\n([poetry](https://python-poetry.org/) is also supported with `poetry install`)\n\n```\n❯ planets --help\nUsage: planets [OPTIONS]\n\nOptions:\n  --wallet TEXT    Planet Wallet, or list of comma separated wallets\n                   [required]\n  --currency TEXT  Currency to convert planets into.\n  --csv            Export csv of all transactions for given wallet\n  --help           Show this message and exit.\n```\n\n\n\n## Examples\n```\n❯ planets --wallet GYLEOJFHACSCATPBVQ345UCMCOMSGV76X4XTVOLHGXKOCJL44YBUAHXJOY --currency eur\n\n\n###### For wallet GYLEOJFHACSCATPBVQ345UCMCOMSGV76X4XTVOLHGXKOCJL44YBUAHXJOY\nThe current price in eur is : 0.254848\namount                426.144000\ncurrent value eur     108.601946\ninitial value eur     62.867696\ngain eur               45.734250\n   amount        date  initial price eur  current value eur  initial value eur  gain eur\n0  23.008  2021-09-15            0.227428           5.863543            5.232664  0.630879\n1  23.040  2021-09-14            0.200080           5.871698            4.609846  1.261852\n2  23.040  2021-09-14            0.200080           5.871698            4.609846  1.261852\n3  23.040  2021-09-12            0.177932           5.871698            4.099553  1.772145\n4  23.040  2021-09-11            0.171145           5.871698            3.943170  1.928528\n5  23.040  2021-09-10            0.159267           5.871698            3.669510  2.202188\n6  22.720  2021-09-09            0.152454           5.790147            3.463757  2.326390\n7  23.040  2021-09-08            0.149045           5.871698            3.433999  2.437699\n8  23.040  2021-09-07            0.146756           5.871698            3.381269  2.490429\n9  23.040  2021-09-06            0.135407           5.871698            3.119766  2.751932\n```\n\nMultiple wallets\n```\n❯ planets --wallet GYLEOJFHACSCATPBVQ345UCMCOMSGV76X4XTVOLHGXKOCJL44YBUAHXJOY,3KBG44MVZSKKOUDW7QJ2QS2FYHFIHNTLT3Q7MTQ2CLG65ZHQ6RL6ENZ7GQ --currency eur\n\n\n###### For wallet GYLEOJFHACSCATPBVQ345UCMCOMSGV76X4XTVOLHGXKOCJL44YBUAHXJOY\nThe current price in eur is : 0.254848\namount                426.144000\ncurrent value eur     108.601946\ninitial value eur     62.867696\ngain eur               45.734250\n   amount        date  initial price eur  current value eur  initial value eur  gain eur\n0  23.008  2021-09-15            0.227428           5.863543            5.232664  0.630879\n1  23.040  2021-09-14            0.200080           5.871698            4.609846  1.261852\n2  23.040  2021-09-14            0.200080           5.871698            4.609846  1.261852\n3  23.040  2021-09-12            0.177932           5.871698            4.099553  1.772145\n4  23.040  2021-09-11            0.171145           5.871698            3.943170  1.928528\n\n\n###### For wallet 3KBG44MVZSKKOUDW7QJ2QS2FYHFIHNTLT3Q7MTQ2CLG65ZHQ6RL6ENZ7GQ\nThe current price in eur is : 0.254848\namount                1740.640000\ncurrent value eur      443.598623\ninitial value eur     199.522137\ngain eur               244.076486\n   amount        date  initial price eur  current value eur  initial value eur  gain eur\n0   23.04  2021-09-15            0.227428           5.871698            5.239942  0.631756\n1   23.04  2021-09-14            0.200080           5.871698            4.609846  1.261852\n2   23.04  2021-09-13            0.185853           5.871698            4.282061  1.589637\n3   23.04  2021-09-12            0.177932           5.871698            4.099553  1.772145\n4   23.04  2021-09-11            0.171145           5.871698            3.943170  1.928528\n```\n\n\n```\n❯ planets --wallet GYLEOJFHACSCATPBVQ345UCMCOMSGV76X4XTVOLHGXKOCJL44YBUAHXJOY --currency usd\n\n###### For wallet GYLEOJFHACSCATPBVQ345UCMCOMSGV76X4XTVOLHGXKOCJL44YBUAHXJOY\nThe current price in usd is : 0.301106\namount                426.144000\ncurrent value usd     128.314515\ninitial value usd     74.360906\ngain usd               53.953609\n   amount        date  initial price usd  current value usd  initial value usd  gain usd\n0  23.008  2021-09-15            0.268778           6.927847            6.184042  0.743805\n1  23.040  2021-09-14            0.236209           6.937482            5.442256  1.495226\n2  23.040  2021-09-14            0.236209           6.937482            5.442256  1.495226\n3  23.040  2021-09-12            0.210221           6.937482            4.843501  2.093982\n4  23.040  2021-09-11            0.202202           6.937482            4.658739  2.278744\n5  23.040  2021-09-10            0.188485           6.937482            4.342697  2.594785\n6  22.720  2021-09-09            0.180454           6.841128            4.099926  2.741202\n7  23.040  2021-09-08            0.176202           6.937482            4.059700  2.877782\n8  23.040  2021-09-07            0.174077           6.937482            4.010729  2.926753\n9  23.040  2021-09-06            0.160621           6.937482            3.700707  3.236775\n```\n\n\n### Export as CSV\n\n```\n❯ planets --wallet GYLEOJFHACSCATPBVQ345UCMCOMSGV76X4XTVOLHGXKOCJL44YBUAHXJOY --currency usd --csv\n```\nWill generate the same output expect it will also create a file called `GYLEOJFHACSCATPBVQ345UCMCOMSGV76X4XTVOLHGXKOCJL44YBUAHXJOY.csv`\n',
    'author': 'errantp',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
