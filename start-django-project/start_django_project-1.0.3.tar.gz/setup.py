# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['start_django_project',
 'start_django_project.django-template',
 'start_django_project.django-template.app',
 'start_django_project.django-template.app.migrations',
 'start_django_project.django-template.project']

package_data = \
{'': ['*'],
 'start_django_project.django-template': ['.vscode/*',
                                          'app/templates/*',
                                          'app/templates/app/*',
                                          'static/CACHE/css/*',
                                          'static/admin/css/*',
                                          'static/admin/css/vendor/select2/*',
                                          'static/admin/fonts/*',
                                          'static/admin/img/*',
                                          'static/admin/img/gis/*',
                                          'static/admin/js/*',
                                          'static/admin/js/admin/*',
                                          'static/admin/js/vendor/jquery/*',
                                          'static/admin/js/vendor/select2/*',
                                          'static/admin/js/vendor/select2/i18n/*',
                                          'static/admin/js/vendor/xregexp/*',
                                          'static/baton/app/*',
                                          'static/baton/app/dist/*',
                                          'static/baton/app/src/*',
                                          'static/baton/app/src/core/*',
                                          'static/baton/app/src/fonts/*',
                                          'static/baton/app/src/img/*',
                                          'static/baton/app/src/styles/*',
                                          'static/baton/img/*',
                                          'static/images/*',
                                          'static/style/*']}

entry_points = \
{'console_scripts': ['start-django-project = start_django_project.cli:cli']}

setup_kwargs = {
    'name': 'start-django-project',
    'version': '1.0.3',
    'description': 'Init a new django project with a simple bootstrap layout',
    'long_description': '# make-django-app\nTo download:\n\n`pip install make-django-project`\n\nTo use:\n\n`start-django-project ./path_of_your_project`\n\nOr to init inside a folder:\n\n`start-django-project ./`',
    'author': 'TechHeart',
    'author_email': 'contact@TechHeart.co.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
