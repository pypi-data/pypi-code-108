# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['jnt_django_toolbox',
 'jnt_django_toolbox.admin',
 'jnt_django_toolbox.admin.decorators',
 'jnt_django_toolbox.admin.fields',
 'jnt_django_toolbox.admin.filters',
 'jnt_django_toolbox.admin.helpers',
 'jnt_django_toolbox.admin.mixins',
 'jnt_django_toolbox.admin.views',
 'jnt_django_toolbox.consts',
 'jnt_django_toolbox.context_managers',
 'jnt_django_toolbox.db',
 'jnt_django_toolbox.db.fields',
 'jnt_django_toolbox.decorators',
 'jnt_django_toolbox.forms',
 'jnt_django_toolbox.forms.fields',
 'jnt_django_toolbox.forms.widgets',
 'jnt_django_toolbox.forms.widgets.readonly',
 'jnt_django_toolbox.helpers',
 'jnt_django_toolbox.management',
 'jnt_django_toolbox.management.commands',
 'jnt_django_toolbox.models',
 'jnt_django_toolbox.models.fields',
 'jnt_django_toolbox.models.fields.bit',
 'jnt_django_toolbox.profiling',
 'jnt_django_toolbox.profiling.db',
 'jnt_django_toolbox.profiling.decorators',
 'jnt_django_toolbox.profiling.profilers',
 'jnt_django_toolbox.templatetags']

package_data = \
{'': ['*'],
 'jnt_django_toolbox': ['static/jnt_django_toolbox/css/autocomplete_filter/*',
                        'static/jnt_django_toolbox/css/widgets/*',
                        'static/jnt_django_toolbox/images/*',
                        'static/jnt_django_toolbox/js/autocomplete_filter/*',
                        'static/jnt_django_toolbox/js/widgets/*',
                        'templates/jnt_django_toolbox/autocomplete_filter/*',
                        'templates/jnt_django_toolbox/widgets/*']}

install_requires = \
['dateparser', 'django>=3.2']

extras_require = \
{'jaeger': ['jaeger-client']}

setup_kwargs = {
    'name': 'jnt-django-toolbox',
    'version': '0.3.7',
    'description': '',
    'long_description': None,
    'author': 'Junte',
    'author_email': 'tech@junte.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
