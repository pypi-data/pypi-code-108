# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lokilogger']

package_data = \
{'': ['*']}

install_requires = \
['colorlog>=6.6.0,<7.0.0']

setup_kwargs = {
    'name': 'lokilogger',
    'version': '1.0.3',
    'description': 'This a custom `logging` for `Loki`',
    'long_description': '# Lokilogger\n\n## Introduction\n\nThis package is just a wrapper around [logging](https://docs.python.org/3/library/logging.html) and [colorlog](https://github.com/borntyping/python-colorlog).\n\n## Installation\n\n```shell\npip install lokilogger\n```\n\n## Usage\n\nAt the start of your program\n\n```python\nfrom lokilogger.logging import set_log_mode\nimport logging\n\nenv = os.getenv("LOGMODE", "DEV")\nset_log_mode("env") # A global setting here, you can set it to `PROD`, `DEV`or `DEV_NO_COLOR`\n```\n\nUse it in other modules\n\n```python\nlogger = logging.getLogger(__name__)\nlogger.error(\'error message\')\n```\n\nOutput\n\nenv=Prod\n\n```shell\n"time": "2022-01-15 07:56:05,440, ""severity": "INFO", "logger": "root","module": "logging", "message": "Dev env is set to production"\n"time": "2022-01-15 07:56:05,440, ""severity": "ERROR", "logger": "__main__","module": "test", "message": "error message"\n"time": "2022-01-15 07:56:05,440, ""severity": "INFO", "logger": "root","module": "test", "message": "error message"\n```\n\nenv=DEV_NO_COLOR\n\n```shell\n2022-01-15 07:54:40,039 | INFO | root | Dev env is set to development without colorlog\n2022-01-15 07:54:40,039 | ERROR | __main__ | error message\n2022-01-15 07:54:40,039 | INFO | root | error message\n```\n',
    'author': 'kangyili',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/polynom-company/lokilogger',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
