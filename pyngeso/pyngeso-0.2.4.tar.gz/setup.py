# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyngeso']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'pyngeso',
    'version': '0.2.4',
    'description': 'Simple python wrapper for the National Grid ESO Portal',
    'long_description': '# pyngeso\n\nSimple python wrapper for the National Grid ESO Portal.\n\n[![](https://img.shields.io/badge/python-3.8-blue.svg)](https://github.com/pyenv/pyenv)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n\n## Getting started\n\n\n* Example usage\n```python\nfrom pyngeso import NgEso\n\nresource = "historic-day-ahead-demand-forecast"\ndate_col = "TARGETDATE"\nstart_date = "2018-01-01"\nend_date = "2018-01-01"\n\nclient = NgEso(resource)\n# returns content of response\nr: bytes = client.query(date_col=date_col, start_date=start_date, end_date=end_date)\n```\n\n## Tested reports\n\n### Queryable via NG\'s api\n* `historic-day-ahead-demand-forecast`\n* `day-ahead-demand-forecast`\n* `historic-2day-ahead-demand-forecast`\n* `2day-ahead-demand-forecast`\n* `historic-day-ahead-wind-forecast`\n* `day-ahead-wind-forecast`\n* `demand-data-update`\n* `dc-results-summary`\n\n### Download of files\n* `historic-generation-mix`\n',
    'author': 'atsangarides',
    'author_email': 'andreas_tsangarides@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/atsangarides/pyngeso',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
