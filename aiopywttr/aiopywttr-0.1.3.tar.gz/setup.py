# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiopywttr']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0', 'pywttr-models>=0.1.1,<0.2.0']

setup_kwargs = {
    'name': 'aiopywttr',
    'version': '0.1.3',
    'description': 'Asynchronous wrapper for wttr.in',
    'long_description': '# aiopywttr\n\n[![Build Status](https://github.com/monosans/aiopywttr/workflows/test/badge.svg?branch=main&event=push)](https://github.com/monosans/aiopywttr/actions?query=workflow%3Atest)\n[![codecov](https://codecov.io/gh/monosans/aiopywttr/branch/main/graph/badge.svg)](https://codecov.io/gh/monosans/aiopywttr)\n[![Python Version](https://img.shields.io/pypi/pyversions/aiopywttr.svg)](https://pypi.org/project/aiopywttr/)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/monosans/aiopywttr/blob/main/LICENSE)\n\nAsynchronous wrapper for [wttr.in](https://wttr.in) weather forecast.\n\nSynchronous version [here](https://github.com/monosans/pywttr).\n\n## Installation\n\n```bash\npython -m pip install aiopywttr\n```\n\n## Example\n\nThis example prints the average temperature in New York today.\n\n```python\nimport asyncio\n\nimport aiopywttr\n\n\nasync def main():\n    forecast = await aiopywttr.en.get_forecast("New York")\n    print(forecast.weather[0].avgtemp_c)\n\n\nasyncio.run(main())\n```\n\nOther languages may also be used instead of `en`. For a complete list of supported languages, see the [file names](https://github.com/monosans/aiopywttr/tree/main/aiopywttr) or follow the code completion in your IDE.\n\n## Documentation\n\nFor an example of type annotations, see `pywttr-models` [README.md](https://github.com/monosans/pywttr-models#usage-for-type-annotation).\n\nThere is no documentation, just follow the code completion from your IDE.\n\nRecommended IDEs:\n\n- [Visual Studio Code](https://code.visualstudio.com) (with [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python))\n- [PyCharm](https://jetbrains.com/pycharm)\n',
    'author': 'monosans',
    'author_email': 'hsyqixco@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/monosans/aiopywttr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
