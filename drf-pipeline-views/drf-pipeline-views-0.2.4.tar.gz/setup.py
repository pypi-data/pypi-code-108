# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pipeline_views']

package_data = \
{'': ['*']}

install_requires = \
['Django>=1.10', 'djangorestframework>=3.7.0']

extras_require = \
{'typing': ['typing-extensions>=4.0']}

setup_kwargs = {
    'name': 'drf-pipeline-views',
    'version': '0.2.4',
    'description': 'Django REST framework views using the pipeline pattern.',
    'long_description': '# Django REST Framework Pipeline Views\n\n[![Coverage Status](https://coveralls.io/repos/github/MrThearMan/drf-pipeline-views/badge.svg?branch=main)](https://coveralls.io/github/MrThearMan/drf-pipeline-views?branch=main)\n[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/MrThearMan/drf-pipeline-views/Tests)](https://github.com/MrThearMan/drf-pipeline-views/actions/workflows/main.yml)\n[![PyPI](https://img.shields.io/pypi/v/drf-pipeline-views)](https://pypi.org/project/drf-pipeline-views)\n[![GitHub](https://img.shields.io/github/license/MrThearMan/drf-pipeline-views)](https://github.com/MrThearMan/drf-pipeline-views/blob/main/LICENSE)\n[![GitHub last commit](https://img.shields.io/github/last-commit/MrThearMan/drf-pipeline-views)](https://github.com/MrThearMan/drf-pipeline-views/commits/main)\n[![GitHub issues](https://img.shields.io/github/issues-raw/MrThearMan/drf-pipeline-views)](https://github.com/MrThearMan/drf-pipeline-views/issues)\n\n\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/drf-pipeline-views)](https://pypi.org/project/drf-pipeline-views)\n[![PyPI - Django Version](https://img.shields.io/pypi/djversions/drf-pipeline-views)](https://pypi.org/project/drf-pipeline-views)\n[![Custom - Django REST Framework Version](https://img.shields.io/badge/drf%20versions-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://pypi.org/project/drf-pipeline-views)\n\n```shell\npip install drf-pipeline-views\n```\n\n---\n\n**Documentation**: [https://mrthearman.github.io/drf-pipeline-views/](https://mrthearman.github.io/drf-pipeline-views/)\n\n**Source Code**: [https://github.com/MrThearMan/drf-pipeline-views](https://github.com/MrThearMan/drf-pipeline-views)\n\n---\n\nInspired by a talk on [The Clean Architecture in Python](https://archive.org/details/pyvideo_2840___The_Clean_Architecture_in_Python)\nby Brandon Rhodes, **drf-pipeline-views** aims to simplify writing testable API endpoints with\n[Django REST framework](https://www.django-rest-framework.org/) using the\n*[Pipeline Design Pattern](https://java-design-patterns.com/patterns/pipeline/)*.\n\nThe main idea behind the pipeline pattern is to process data in steps. Input from the previous step\nis passed to the next, resulting in a collection of "data-in, data-out" -functions. These functions\ncan be easily unit tested, since none of the functions depend on the state of the objects in the other parts\nof the pipeline. Furthermore, IO can be separated into its own step, making the other parts of the\nlogic simpler and faster to test by not having to mock or do any other special setup around the IO.\nThis also means that the IO block, or in fact any other part of the application, can be replaced as long as the\ndata flowing through the pipeline remains the same.\n\nHave a look at the [quickstart](https://mrthearman.github.io/drf-pipeline-views/quickstart)\nsection in the documentation on basic usage.\n',
    'author': 'Matti Lamppu',
    'author_email': 'lamppu.matti.akseli@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MrThearMan/drf-pipeline-views',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
