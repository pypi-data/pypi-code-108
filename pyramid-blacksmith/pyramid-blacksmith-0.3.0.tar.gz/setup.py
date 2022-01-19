# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pyramid_blacksmith']

package_data = \
{'': ['*']}

install_requires = \
['blacksmith>=0.12.1,<0.13.0', 'pyramid>=2.0,<3.0']

extras_require = \
{':extra == "prometheus"': ['prometheus-client>=0.12.0,<0.13.0']}

setup_kwargs = {
    'name': 'pyramid-blacksmith',
    'version': '0.3.0',
    'description': 'Pyramid Bindings for Blacksmith',
    'long_description': 'pyramid-blacksmith\n==================\n\n.. image:: https://readthedocs.org/projects/pyramid-blacksmith/badge/?version=latest\n   :target: https://pyramid-blacksmith.readthedocs.io/en/latest/?badge=latest\n   :alt: Documentation Status\n\n.. image:: https://github.com/mardiros/pyramid-blacksmith/actions/workflows/main.yml/badge.svg\n   :target: https://github.com/mardiros/pyramid-blacksmith/actions/workflows/main.yml\n   :alt: Continuous Integration\n\n.. image:: https://codecov.io/gh/mardiros/pyramid-blacksmith/branch/main/graph/badge.svg?token=9IRABRO2LN\n   :target: https://codecov.io/gh/mardiros/pyramid-blacksmith\n   :alt: Coverage\n\nPyramid bindings for `Blacksmith`_ rest api client.\n\n\nIntroduction\n------------\n\nThis plugin create a request proterty named ``blacksmith`` that bind\nclients to do API Call using `Blacksmith`_.\n\n\nClients are configured via the pyramid configurator and its settings.\n\nThen you can access the client factory behind a blacksmith property of\nthe request.\n\n\n::\n\n   def my_view(request):\n      api_dummy = request.blacksmith.client("api_dummy")\n      dummy = api_dummy.dummies.get({"name": "alice"})\n\n\nIn the example above, a dummy resource has been fetch using the service api_dummy.\nThe client method is a configured `Blacksmith Factory`_.\n\nThe configuration of the factory is simply made throw the pyramid configurator.\n\nGo ahead and `get familiar with the documentation`_.\n\n\n.. _`Blacksmith`: https://python-blacksmith.readthedocs.io/en/latest/index.html\n.. _`Blacksmith Factory`: https://python-blacksmith.readthedocs.io/en/latest/user/instanciating_client.html#instanciating-client\n.. _`get familiar with the documentation`: https://pyramid-blacksmith.readthedocs.io/\n\n',
    'author': 'Guillaume Gauvrit',
    'author_email': 'guillaume@gauvr.it',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mardiros/pyramid-blacksmith',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
