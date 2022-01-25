# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['uploadgrampyapi']
setup_kwargs = {
    'name': 'uploadgrampyapi',
    'version': '1.5',
    'description': 'This API can be upload, download, remove and rename any files from the service uploadgram.me. More on my GitHub: https://github.com/tankalxat34/UploadgramPyAPI',
    'long_description': None,
    'author': 'tankalxat34',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
