# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['helpers']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.4,<0.5.0']

setup_kwargs = {
    'name': 'pylib-helpers',
    'version': '0.3.20',
    'description': 'Helpers for common functional work done across several projects',
    'long_description': '# pylib-helpers\n\nHelpers for logging, sleeping, and other common functional work done across projects\n\n[![Release](https://github.com/samarthj/pylib-helpers/actions/workflows/release.yml/badge.svg)](https://github.com/samarthj/pylib-helpers/actions/workflows/release.yml)\n[![GitHub release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/samarthj/pylib-helpers?sort=semver)](https://github.com/samarthj/pylib-helpers/releases)\n[![PyPI](https://img.shields.io/pypi/v/pylib-helpers)](https://pypi.org/project/pylib-helpers/)\n\n[![Build](https://github.com/samarthj/pylib-helpers/actions/workflows/build_matrix.yml/badge.svg)](https://github.com/samarthj/pylib-helpers/actions/workflows/build_matrix.yml)\n\n[![Total alerts](https://img.shields.io/lgtm/alerts/g/samarthj/pylib-helpers.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/samarthj/pylib-helpers/alerts/)\n[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/samarthj/pylib-helpers.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/samarthj/pylib-helpers/context:python)\n\n[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)\n\n## RetryHandler\n\nSamples can be found here in the [tests](https://github.com/samarthj/pylib-helpers/blob/main/tests/test_retry_handler.py)\n\nExample usage:\n\n```python\n\nfrom somelib import ClientError\nfrom helpers import Logger, RetryHandler, Sleeper\n\nLOGGER = Logger()\nSLEEPER = Sleeper()\n\ndef _client_error(err_obj):\n    err_msg = str(err_obj)\n    if "Recoverable" not in err_msg:\n        raise err_obj\n    else:\n        LOGGER.print_error(err_msg)\n        SLEEPER.normal_sleep()\n\n@RetryHandler(\n    (ClientError),\n    max_retries=10,\n    wait_time=0,\n    err_callbacks={"ClientError": (_client_error, {})},\n).wrap\ndef do_the_thing(data):\n    pass\n```\n',
    'author': 'Sam',
    'author_email': 'dev@samarthj.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/samarthj/pylib-helpers',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
