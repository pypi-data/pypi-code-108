# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['celery_yaml']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'celery>=4']

extras_require = \
{'pyramid': ['pyramid>=1.9', 'plaster-yaml>=0.1.3,<0.2.0']}

setup_kwargs = {
    'name': 'celery-yaml',
    'version': '0.3.0',
    'description': 'Easy configuration for celery app using Yaml file',
    'long_description': '# Easy Configuration For Celery App Using a Yaml File\n\n`celery-yaml` is a library to inject a --yaml option to the `celery worker`\ncommand in order to inject its configuration.\n\nIt also handle help to configurate this application for Pyramid application.\n\n## Usage\n\n### With Celery 4\n\n```sh\ncelery worker -A my_application.module_containing_my.app --yaml development.yaml ...\n```\n\n### With Celery 5\n\n```sh\ncelery -A my_application.module_containing_my.app worker --yaml development.yaml ...\n```\n\n\nThis will configure the application `my_application` containing an application\n`app` in a submodule `module_containing_my`.\n\nThe celery app must register the `--yaml` using the `add_yaml_option` on the\napp instance, this way:\n\n```python\nfrom celery import Celery\nfrom celery_yaml import add_yaml_option\n\napp = Celery()\nadd_yaml_option(app)\n```\n\n### Yaml format\n\n```yaml\ncelery:\n  broker_url: \'amqp://guest:guest@localhost:5672//\'\n  result_backend: \'rpc://\'\n  imports:\n      - my_application.tasks\n  # see all settings in the celery docs: \n  # https://docs.celeryproject.org/en/stable/userguide/configuration.html\n\nlogging:\n  version: 1\n  # dictConfig format\n  # https://docs.python.org/3/library/logging.config.html#logging-config-dictschema\n```\n\n---\n**NOTE**\n\nThe broker_url can also be override by an environment variable `CELERY_BROKER_URL`\nto avoid password in the configuration file.\n---\n\n## Using Celery in a Pyramid App.\n\nThe extras "pyramid" must be added to install the extras depencencies.\n\n### With poetry\n\n```toml\n[tool.poetry.dependencies]\ncelery-yaml = { version = "^0.1.3", extras = ["pyramid"] }\n```\n\nThen some entry_points have to configure, such as:\n\n```toml\n[tool.poetry.plugins."paste.app_factory"]\nmain = "pyramid_app.wsgi:main"\n\n[tool.poetry.plugins."celery_yaml.app"]\nmain = "pyramid_app.backend:app"\n\n[tool.poetry.plugins."plaster.loader_factory"]\n"file+yaml" = "plaster_yaml:Loader"\n```\n\nthe `paste.app_factory` is used by `Pyramid` itself to build the WSGI\nsergivice but we add a `plaster.loader_factory` to configure the usage\nof a yaml file instead of an `ini` file to configure it.\n\nThen the `celery_yaml.app` is used by `celery-yaml` as an entrypoint to\nthe celery app.\n\n\nThen, in the configuration file,\n\n```yaml\ncelery: &celery\n  result_backend: \'rpc://\'\n  imports:\n      - pyramid_app.tasks\n\napp:\n  "use": "egg:pyramid_app"\n  "pyramid.includes": ["celery_yaml"]\n  "celery":\n    <<: *celery\n    "use": "egg:pyramid_app"\n\n```\n\n#### See full example in the examples directory:\n\n##### Pyramid with Celery 4\nhttps://github.com/mardiros/celery-yaml/tree/master/examples/pyramid-app\n\n##### Pyramid with Celery 5\n\nhttps://github.com/mardiros/celery-yaml/tree/master/examples/pyramid-app5\n',
    'author': 'Guillaume Gauvrit',
    'author_email': 'guillaume@gauvr.it',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
