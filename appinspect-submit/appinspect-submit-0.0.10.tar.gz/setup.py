# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['appinspect_submit']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0', 'loguru>=0.5.3,<0.6.0', 'requests>=2.27.1,<3.0.0']

entry_points = \
{'console_scripts': ['appinspect-submit = appinspect_submit.__main__:cli']}

setup_kwargs = {
    'name': 'appinspect-submit',
    'version': '0.0.10',
    'description': 'Submits your app to Splunk AppInspect.',
    'long_description': '# appinspect-submit\n\nA simple CLI for submitting your Splunk app package to AppInspect and reading the report.\n\n\n# Installation\n\n`pip install appinspect-submit`\n\n# Usage\n\n`$ appinspect-submit [OPTIONS] FILENAME`\n\nUploads your Splunk app package to the AppInspect service and downloads the report. Report filename will look like "%Y%m%d-%H%M%S-report.json\n\n## Options:\n    --test-future                   Use the \'future\' tests\n    --help                          Show this message and exit.\n',
    'author': 'James Hodgkinson',
    'author_email': 'james@terminaloutcomes.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/terminaloutcomes/appinspect-submit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
