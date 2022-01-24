# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['librelingo_yaml_loader']

package_data = \
{'': ['*']}

install_requires = \
['Markdown>=3.3.4,<4.0.0',
 'bleach-whitelist>=0.0.11,<0.0.12',
 'bleach>=4.0.0,<5.0.0',
 'click>=8.0.0,<9.0.0',
 'html2markdown>=0.1.7,<0.2.0',
 'librelingo-types>=3.3.0,<4.0.0',
 'pyfakefs>=4.3.3,<5.0.0',
 'pyyaml>=5.3.1,<6.0.0',
 'snapshottest>=0.6.0,<0.7.0']

extras_require = \
{'hunspell': ['hunspell>=0.5.5,<0.6.0']}

setup_kwargs = {
    'name': 'librelingo-yaml-loader',
    'version': '1.9.1',
    'description': 'Load YAML-based LibreLingo courses in your Python project.',
    'long_description': '<a id="librelingo_yaml_loader.yaml_loader"></a>\n\n# librelingo\\_yaml\\_loader.yaml\\_loader\n\n<a id="librelingo_yaml_loader.yaml_loader.load_course"></a>\n\n#### load\\_course\n\n```python\ndef load_course(path: str)\n```\n\nLoad a YAML-based course into a Course() object\n\n',
    'author': 'Dániel Kántor',
    'author_email': 'git@daniel-kantor.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
