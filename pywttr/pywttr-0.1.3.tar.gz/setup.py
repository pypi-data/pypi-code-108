# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pywttr']

package_data = \
{'': ['*']}

install_requires = \
['pywttr-models>=0.1.1,<0.2.0', 'requests>=2.25.1,<3.0.0']

setup_kwargs = {
    'name': 'pywttr',
    'version': '0.1.3',
    'description': 'Wrapper for wttr.in',
    'long_description': '# pywttr\n\n[![Build Status](https://github.com/monosans/pywttr/workflows/test/badge.svg?branch=main&event=push)](https://github.com/monosans/pywttr/actions?query=workflow%3Atest)\n[![codecov](https://codecov.io/gh/monosans/pywttr/branch/main/graph/badge.svg)](https://codecov.io/gh/monosans/pywttr)\n[![Python Version](https://img.shields.io/pypi/pyversions/pywttr.svg)](https://pypi.org/project/pywttr/)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/monosans/pywttr/blob/main/LICENSE)\n\nWrapper for [wttr.in](https://wttr.in) weather forecast.\n\nAsynchronous version [here](https://github.com/monosans/aiopywttr).\n\n## Installation\n\n```bash\npython -m pip install pywttr\n```\n\n## Example\n\nThis example prints the average temperature in New York today.\n\n```python\nimport pywttr\n\nforecast = pywttr.en.get_forecast("New York")\nprint(forecast.weather[0].avgtemp_c)\n```\n\nOther languages may also be used instead of `en`. For a complete list of supported languages, see the [file names](https://github.com/monosans/pywttr/tree/main/pywttr) or follow the code completion in your IDE.\n\n## Documentation\n\nFor an example of type annotations, see `pywttr-models` [README.md](https://github.com/monosans/pywttr-models#usage-for-type-annotation).\n\nThere is no documentation, just follow the code completion from your IDE.\n\nRecommended IDEs:\n\n- [Visual Studio Code](https://code.visualstudio.com) (with [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python))\n- [PyCharm](https://jetbrains.com/pycharm)\n',
    'author': 'monosans',
    'author_email': 'hsyqixco@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/monosans/pywttr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
