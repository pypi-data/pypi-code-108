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
                                          'static/images/*',
                                          'static/style/*']}

entry_points = \
{'console_scripts': ['start-django-project = start_django_project.cli:cli']}

setup_kwargs = {
    'name': 'start-django-project',
    'version': '1.0.4',
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
