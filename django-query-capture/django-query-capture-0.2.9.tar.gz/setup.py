# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_query_capture', 'django_query_capture.presenter']

package_data = \
{'': ['*']}

install_requires = \
['Django>=2.2', 'Pygments>=2.11.2,<3.0.0', 'tabulate>=0.8.9,<0.9.0']

entry_points = \
{'console_scripts': ['django-query-capture = '
                     'django_query_capture.__main__:app']}

setup_kwargs = {
    'name': 'django-query-capture',
    'version': '0.2.9',
    'description': 'Shows queries, detects N+1 in Django, Simple to use, Can Customize Console Result',
    'long_description': '# django-query-capture\n\n[![Build status](https://github.com/ashekr/django-query-capture/workflows/build/badge.svg?branch=main&event=push)](https://github.com/ashekr/django-query-capture/actions?query=workflow%3Abuild)\n[![Python Version](https://img.shields.io/pypi/pyversions/django-query-capture.svg)](https://pypi.org/project/django-query-capture/)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/ashekr/django-query-capture/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)\n[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/ashekr/django-query-capture/blob/main/.pre-commit-config.yaml)\n[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/ashekr/django-query-capture/releases)\n[![License](https://img.shields.io/github/license/ashekr/django-query-capture)](https://github.com/ashekr/django-query-capture/blob/main/LICENSE)\n![Coverage Report](assets/images/coverage.svg)\n\n\n## Overview\n\n![img.png](assets/images/main.png)\n\nDjango Query Capture can check the query situation at a glance, notice slow queries, and notice where N+1 occurs.\n\nSome reasons you might want to use django-query-capture:\n\n- It can be used to simply check queries in a specific block.\n- It supports Django Middleware, Context Manager, and Decorator.\n- When you use Context Manager, you can get real-time query data.\n- You can see where the query occurs.\n- Inefficient queries can be found in the test code.\n- It is easy to customize by simply changing the table shape, changing the color, and selecting and setting the desired output.\n- It supports customization that allows you to decorate the output freely from the beginning.\n- Fully Documented\n- It supports Type hint everywhere.\n\n## Simple Usage\n\n- Just add it to Middleware without any other settings, and it will be output whenever a query occurs.\n\n```python\nMIDDLEWARE = [\n  ...,\n  "django_query_capture.middleware.QueryCaptureMiddleware",\n]\n```\n\n- Use in function-based views. or just function\n\n```python\nfrom django_query_capture import query_capture\n\n@query_capture()\ndef my_view(request):\n  pass\n```\n\n- Use in class-based views.\n\n```python\nfrom django.utils.decorators import method_decorator\nfrom django.views.generic import TemplateView\nfrom django_query_capture import query_capture\n\n@method_decorator(query_capture, name=\'dispatch\')\nclass AboutView(TemplateView):\n  pass\n```\n\n- Use it as a context.\n\nWhen used as Context, you can check the query in real time.\n\n```python\nfrom django_query_capture import query_capture\n\nfrom tests.news.models import Reporter\n\n@query_capture()\ndef run_something():\n    with query_capture() as capture:\n        Reporter.objects.create(full_name=f"target-1")\n        print(len(capture.captured_queries))  # console: 1\n        Reporter.objects.create(full_name=f"target-2")\n        print(len(capture.captured_queries))  # console: 2\n```\n\n- Use in test\n\nTest code can capture inefficient queries through the `AssertInefficientQuery` Util.\n\n\n```python\nfrom django.test import TestCase\n\nfrom django_query_capture.test_utils import AssertInefficientQuery\n\n\nclass AssertInefficientQueryTests(TestCase):\n    def test_assert_inefficient_query(self):\n          with AssertInefficientQuery(self, num=19):\n            self.client.get(\'/api/reporter\')  # desire threshold count 19 but, /api/reporter duplicate query: 20, so raise error\n```\n\n## Installation\n\n```bash\npip install -U django-query-capture\n```\n\nor install with `Poetry`\n\n```bash\npoetry add django-query-capture\n```\n\n## Full Documentation\n\nExtension documentation is found here: [https://ashekr.github.io/django-query-capture/](https://ashekr.github.io/django-query-capture/).\n\n## 🛡 License\n\n[![License](https://img.shields.io/github/license/ashekr/django-query-capture)](https://github.com/ashekr/django-query-capture/blob/main/LICENSE)\n\nThis project is licensed under the terms of the `MIT` license. See [LICENSE](https://github.com/ashekr/django-query-capture/blob/main/LICENSE) for more details.\n\n## Credits [![🚀 Your next Python package needs a bleeding-edge project structure.](https://img.shields.io/badge/python--package--template-%F0%9F%9A%80-brightgreen)](https://github.com/TezRomacH/python-package-template)\n\nThis project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template)\n',
    'author': 'AsheKR',
    'author_email': 'tech@ashe.kr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ashekr/django-query-capture',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
