# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xmltojson', 'xmltojson.scripts']

package_data = \
{'': ['*']}

install_requires = \
['xmltodict>=0.12.0,<0.13.0']

entry_points = \
{'console_scripts': ['xmltojson = xmltojson.scripts.cli:main']}

setup_kwargs = {
    'name': 'xmltojson',
    'version': '2.0.1',
    'description': 'A Python module and cli tool to quickly convert xml text or files into json',
    'long_description': '# xmltojson\n\n---\n\nPython library and cli tool for converting XML to JSON\n\n[![Downloads](https://static.pepy.tech/personalized-badge/xmltojson?period=total&units=international_system&left_color=lightgrey&right_color=brightgreen&left_text=Installs)](https://pepy.tech/project/xmltojson)\n\n## Install\n\n`$ poetry add xmltojson`\n\n`$ pip install xmltojson`\n\n## Usage\n\n### Command line:\n\n#### Converting an XML file and sending the output to STDOUT\n`$ xmltojson <filename.xml>`\n\n#### Send output to a file\n`$ xmltojson <filename.xml> -o <new_filename.json>`\n\n#### xmltojson can also read from STDIN\n`$ echo \'<name>John</name>\' | xmltojson --stdin`\n\n### Library:\n```\n[1]: import xmltojson\n[2]: with open(\'/path/to/file\', \'r\') as f:\n...:     my_xml = f.read()\n[3]: xmltojson.parse(my_xml)\n\'{"name": "John"}\'\n```\n',
    'author': 'John Shanahan',
    'author_email': 'shanahan.jrs@gmail.com',
    'maintainer': 'John Shanahan',
    'maintainer_email': 'shanahan.jrs@gmail.com',
    'url': 'https://github.com/shanahanjrs/xmltojson',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
