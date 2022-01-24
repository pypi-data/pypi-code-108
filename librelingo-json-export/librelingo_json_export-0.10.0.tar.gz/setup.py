# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['librelingo_json_export']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0.0,<8.0.4',
 'editdistance>=0.6.0,<0.7.0',
 'librelingo-types>=3.0.0,<4.0.0',
 'librelingo-utils>=2.6.0,<3.0.0',
 'librelingo-yaml-loader>=1.0.0,<2.0.0',
 'python-slugify>=4.0.1,<5.0.0']

extras_require = \
{'hunspell': ['hunspell>=0.5.5,<0.6.0']}

entry_points = \
{'console_scripts': ['librelingo-export-cli = librelingo_json_export.cli:main']}

setup_kwargs = {
    'name': 'librelingo-json-export',
    'version': '0.10.0',
    'description': 'Export LibreLingo courses in the JSON format used by the web app',
    'long_description': '<a name="librelingo_json_export.export"></a>\n# librelingo\\_json\\_export.export\n\n<a name="librelingo_json_export.export.export_course"></a>\n#### export\\_course\n\n```python\nexport_course(export_path: str, course: Course, settings=None)\n```\n\nWrites the course to JSON files in the specified path.\n\n### Usage example:\n\n```python\nfrom librelingo_yaml_loader import load_course\nfrom librelingo_json_export.export import export_course\n\ncourse = load_course("./courses/french-from-english")\nexport_course("./apps/web/src/courses/french-from-english", course)\n```\n\n',
    'author': 'Dániel Kántor',
    'author_email': 'git@daniel-kantor.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
