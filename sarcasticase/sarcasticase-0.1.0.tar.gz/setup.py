# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['sarcasticase']
entry_points = \
{'console_scripts': ['sarcasticase = sarcasticase:main']}

setup_kwargs = {
    'name': 'sarcasticase',
    'version': '0.1.0',
    'description': 'Easily convert text to be like sarcastic Spongebob',
    'long_description': '#  sarcasticase\n\n[![PyPI version](https://img.shields.io/pypi/v/sarcasticase)](https://pypi.org/project/sarcasticase/)\n[![Python Versions](https://img.shields.io/pypi/pyversions/sarcasticase)](https://pypi.org/project/sarcasticase/)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n### Usage\n\n#### install\npip install sarcasticase\n\n#### command line\n```sh\n$ sarcasticase i know you are but what am i\n> i KnOw YoU aRe BuT wHaT aM i\n```\n\n#### import function\n```sh\nfrom sarcasticase import sarcasticase\nsarcastic_text = sarcasticase("i know you are but what am i")\n```\n\n## Change Log\n\n### [0.1.0] - 2022-01-27\n\n- initial release\n',
    'author': 'Kyle Smith',
    'author_email': 'smithk86@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/smithk86/sarcasticase/',
    'py_modules': modules,
    'entry_points': entry_points,
    'python_requires': '>=3.0,<4.0',
}


setup(**setup_kwargs)
