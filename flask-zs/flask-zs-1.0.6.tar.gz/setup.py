# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flask_zs', 'flask_zs.bin']

package_data = \
{'': ['*']}

install_requires = \
['Flask', 'requests']

extras_require = \
{'all': ['zs-mixins', 'flask-http-client'],
 'http-client': ['flask-http-client'],
 'mixins': ['zs-mixins']}

entry_points = \
{'console_scripts': ['collect-models = flask_zs.bin.collect_models:main']}

setup_kwargs = {
    'name': 'flask-zs',
    'version': '1.0.6',
    'description': 'A helpers for Flask.',
    'long_description': 'Helpers for Flask.\n====================\n\nHelpers for Flask. 使用示例 `codeif/flask-zs-template  <https://github.com/codeif/flask-zs-template>`_\n\n依赖:\n\n- flask\n- requests\n\n\n安装\n----\n\n.. code-block:: sh\n\n    pip install flask-zs\n\n额外安装 `codeif/zs-mixins <https://github.com/codeif/zs-mixins>`_\n\n.. code-block:: sh\n\n    pip install flask-zs[mixins]\n\n\n集中models\n-------------\n\n把models集中到一个__init__.py中(zsdemo为package name)::\n\n    PYTHONPATH=. collect-models <zsdemo> instance/__init__.py\n',
    'author': 'codeif',
    'author_email': 'me@codeif.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/codeif/flask-zs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
