# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['drfexts', 'drfexts.filtersets', 'drfexts.serializers']

package_data = \
{'': ['*']}

install_requires = \
['django-filter>=21.1',
 'django-storages',
 'django>=3.0',
 'djangorestframework-csv>=2.1.1,<3.0.0',
 'djangorestframework>=3.12.4',
 'openpyxl>=3.0.9,<4.0.0',
 'pip>=21.3.1,<22.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'ujson>=5.1.0,<6.0.0']

setup_kwargs = {
    'name': 'drfexts',
    'version': '0.3.2',
    'description': 'Django Restframework Utils',
    'long_description': "drfexts\n=======\n\n[![GitHub license](https://img.shields.io/github/license/aiden520/drfexts)](https://github.com/aiden520/drfexts/blob/master/LICENSE)\n[![pypi-version](https://img.shields.io/pypi/v/drfexts.svg)](https://pypi.python.org/pypi/drfexts)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/drfexts)\n[![PyPI - Django Version](https://img.shields.io/badge/django-%3E%3D3.0-44B78B)](https://www.djangoproject.com/)\n[![PyPI - DRF Version](https://img.shields.io/badge/djangorestframework-%3E%3D3.0-red)](https://www.django-rest-framework.org)\n[![Build Status](https://app.travis-ci.com/aiden520/drfexts.svg?branch=master)](https://app.travis-ci.com/aiden520/drfexts)\n\n**Extensions for Django REST Framework**\n\n**Author:** aiden lu\n\nInstallation\n------------\n\n``` {.bash}\n$ pip install drfexts\n```\n\nUsage\n-----\n\n*views.py*\n\n``` {.python}\nfrom rest_framework.views import APIView\nfrom rest_framework.settings import api_settings\nfrom drfexts.viewsets import ExportMixin\n\nclass MyView (ExportMixin, APIView):\n    ...\n```\n\nOrdered Fields\n--------------\n\nBy default, a `CSVRenderer` will output fields in sorted order. To\nspecify an alternative field ordering you can override the `header`\nattribute. There are two ways to do this:\n\n1)  Create a new renderer class and override the `header` attribute\n    directly:\n\n    > ``` {.python}\n    > class MyUserRenderer (CSVRenderer):\n    >     header = ['first', 'last', 'email']\n    >\n    > @api_view(['GET'])\n    > @renderer_classes((MyUserRenderer,))\n    > def my_view(request):\n    >     users = User.objects.filter(active=True)\n    >     content = [{'first': user.first_name,\n    >                 'last': user.last_name,\n    >                 'email': user.email}\n    >                for user in users]\n    >     return Response(content)\n    > ```\n\n2)  Use the `renderer_context` to override the field ordering on the\n    fly:\n\n    > ``` {.python}\n    > class MyView (APIView):\n    >     renderer_classes = [CSVRenderer]\n    >\n    >     def get_renderer_context(self):\n    >         context = super().get_renderer_context()\n    >         context['header'] = (\n    >             self.request.GET['fields'].split(',')\n    >             if 'fields' in self.request.GET else None)\n    >         return context\n    >\n    >     ...\n    > ```\n\nLabeled Fields\n--------------\n\nCustom labels can be applied to the `CSVRenderer` using the `labels`\ndict attribute where each key corresponds to the header and the value\ncorresponds to the custom label for that header.\n\n1\\) Create a new renderer class and override the `header` and `labels`\nattribute directly:\n\n> ``` {.python}\n> class MyBazRenderer (CSVRenderer):\n>     header = ['foo.bar']\n>     labels = {\n>         'foo.bar': 'baz'\n>     }\n> ```\n\nPagination\n----------\n\nUsing the renderer with paginated data is also possible with the new\n[PaginatedCSVRenderer]{.title-ref} class and should be used with views\nthat paginate data\n\nFor more information about using renderers with Django REST Framework,\nsee the [API\nGuide](http://django-rest-framework.org/api-guide/renderers/) or the\n[Tutorial](http://django-rest-framework.org/tutorial/1-serialization/).\n\nRunning the tests\n-----------------\n\nTo run the tests against the current environment:\n\n``` {.bash}\n$ ./manage.py test\n```\n\n### Changelog\n\n1.0.0\n-----\n\n-   Initial release\n\n## Thanks\n\n[![PyCharm](docs/pycharm.svg)](https://www.jetbrains.com/?from=drfexts)",
    'author': 'aiden',
    'author_email': 'allaher@icloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/aiden520/drfexts',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
