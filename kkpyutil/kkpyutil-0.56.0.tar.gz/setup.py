# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['kkpyutil']
setup_kwargs = {
    'name': 'kkpyutil',
    'version': '0.56.0',
    'description': 'Personal utility functions and classes frequently used by myself for daily Python work.',
    'long_description': '# kkpyutil\nPersonal utility functions and classes frequently used by myself for daily Python work.\n\nIt does not necessarily benefit everybody, but I hope it \nmay occasionally shed light on some issues you may have in your own work.\n\n## INSTALL\n\n```shell\npip3 install kkpyutil\n```\n',
    'author': 'Beinan Li',
    'author_email': 'li.beinan@gmail.com',
    'maintainer': 'Beinan Li',
    'maintainer_email': 'li.beinan@gmail.com',
    'url': 'https://github.com/kakyoism/kkpyutil/',
    'py_modules': modules,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
