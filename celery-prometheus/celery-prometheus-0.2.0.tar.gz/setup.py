# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['celery_prometheus']

package_data = \
{'': ['*']}

install_requires = \
['celery>=4']

setup_kwargs = {
    'name': 'celery-prometheus',
    'version': '0.2.0',
    'description': 'Celery with your own prometheus metrics',
    'long_description': 'Celery Prometheus\n=================\n\nAdd you own metrics to your celery backend.\n\n\n\nUsage:\n\n::\n\n    app = Celery()\n    add_prometheus_option(app)\n\n\nThen, using Celery 4.\n\n\n::\n    \n     export PROMETHEUS_MULTIPROC_DIR=/var/cache/my_celery_app\n     celery worker -A sequoia_api_notif.backend --prometheus-collector-addr 0.0.0.0:6543\n\n\nThis will expose the metrics on 0.0.0.0:6543 of the host than can be scrapped by\nprometheus.',
    'author': 'Guillaume Gauvrit',
    'author_email': 'guillaume@gandi.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
