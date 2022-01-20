# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['beeline',
 'beeline.middleware',
 'beeline.middleware.awslambda',
 'beeline.middleware.bottle',
 'beeline.middleware.django',
 'beeline.middleware.flask',
 'beeline.middleware.werkzeug',
 'beeline.patch',
 'beeline.propagation']

package_data = \
{'': ['*']}

install_requires = \
['libhoney>=1.7.0', 'wrapt>=1.12.1,<2.0.0']

entry_points = \
{'console_scripts': ['tests = beeline.test_suite:run_tests']}

setup_kwargs = {
    'name': 'honeycomb-beeline',
    'version': '3.1.0',
    'description': 'Honeycomb library for easy instrumentation',
    'long_description': '# Honeycomb Beeline for Python\n\n[![OSS Lifecycle](https://img.shields.io/osslifecycle/honeycombio/beeline-python?color=success)](https://github.com/honeycombio/home/blob/main/honeycomb-oss-lifecycle-and-practices.md)\n[![Build Status](https://circleci.com/gh/honeycombio/beeline-python.svg?style=svg)](https://app.circleci.com/pipelines/github/honeycombio/beeline-python)\n\nThis package makes it easy to instrument your Python web application to send useful events to [Honeycomb](https://honeycomb.io), a service for debugging your software in production.\n\n- [Usage and Examples](https://docs.honeycomb.io/getting-data-in/beelines/beeline-python/)\n- [API Reference](https://honeycombio.github.io/beeline-python/)\n\n## Compatible with\n\nCurrently, supports Django (>2), Flask, Bottle, and Tornado.\n\nCompatible with Python 3.\n\n## Get in touch\n\nPlease reach out to [support@honeycomb.io](mailto:support@honeycomb.io) or ping\nus with the chat bubble on [our website](https://www.honeycomb.io) for any\nassistance. We also welcome [bug reports](https://github.com/honeycombio/beeline-python/issues).\n\n## Contributions\n\nFeatures, bug fixes and other changes to `beeline-python` are gladly accepted. Please\nopen issues or a pull request with your change. Remember to add your name to the\nCONTRIBUTORS file!\n\nIf you add a new test module, be sure and update `beeline.test_suite` to pick up the new tests.\n\nAll contributions will be released under the Apache License 2.0.\n',
    'author': 'Honeycomb.io',
    'author_email': 'feedback@honeycomb.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/honeycombio/beeline-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4',
}


setup(**setup_kwargs)
