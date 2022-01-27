# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['subtitle_parser']
setup_kwargs = {
    'name': 'subtitle-parser',
    'version': '0.1.0',
    'description': 'Parser for SRT and WebVTT subtitle files',
    'long_description': 'subtitle-parser\n===============\n\nThis is a simple Python library for parsing subtitle files in SRT or WebVTT format.\n',
    'author': 'Remi Rampin',
    'author_email': 'remi@rampin.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/remram44/subtitle-parser',
    'py_modules': modules,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
