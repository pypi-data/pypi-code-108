# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'examples'}

packages = \
['sml']

package_data = \
{'': ['*']}

modules = \
['sml-mqtt-bridge', 'test_asyncio']
install_requires = \
['async-timeout>=4.0', 'bitstring>=3.1', 'pyserial-asyncio>=0.6']

setup_kwargs = {
    'name': 'pysml',
    'version': '0.0.7',
    'description': 'Python library for EDL21 smart meters using Smart Message Language (SML)',
    'long_description': '# pysml\nPython library for EDL21 smart meters using Smart Message Language (SML)\n',
    'author': 'Andreas Oberritter',
    'author_email': 'obi@saftware.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
